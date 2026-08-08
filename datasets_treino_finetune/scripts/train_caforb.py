#!/usr/bin/env python3
"""
train_caforb.py — Phase 5: LoRA fine-tuning of google/gemma-4-12B-it-qat-w4a16-ct
on the CaForB dataset.

The base model is pre-quantized (QAT w4a16) — weights are already 4-bit and frozen.
Only LoRA adapters are trained, keeping VRAM usage under 8 GB on RTX 4070.

Requirements:
    python scripts/setup_ml.py   # one-time install

Usage:
    python scripts/train_caforb.py                    # Full training (3 epochs)
    python scripts/train_caforb.py --test             # Quick test (50 steps)
    python scripts/train_caforb.py --epochs 1         # 1 epoch only
    python scripts/train_caforb.py --resume checkpoints/checkpoint-100

Output:
    caforb-lora/               — LoRA adapter weights (ready for merge)
    caforb-lora/training.log   — Loss curve
"""

import os
import sys
import json
import time
import math
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    TrainerCallback,
    DataCollatorForLanguageModeling,
)
from peft import (
    LoraConfig,
    get_peft_model,
    TaskType,
)

# ──────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
TRAIN_PATH = BASE_DIR / "final" / "train.jsonl"
VAL_PATH = BASE_DIR / "final" / "validation.jsonl"
OUTPUT_DIR = BASE_DIR / "caforb-lora"

# Gemma 4 E2B (2.3B effective, 5.1B total) — instruction-tuned
MODEL_NAME = "google/gemma-4-E2B-it"

# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────

LORA_R = 16                 # LoRA rank
LORA_ALPHA = 16             # Scaling factor
LORA_DROPOUT = 0.05         # Regularization
MAX_SEQ_LENGTH = 2048       # Fits comfortably in 8GB with 2.3B E2B model
BATCH_SIZE = 1              # Per-device (keep at 1 for 8GB)
GRAD_ACCUM = 4              # Effective batch = 4
NUM_EPOCHS = 3              # Full passes over dataset
LEARNING_RATE = 2e-4        # Standard LoRA LR
WARMUP_RATIO = 0.03
LR_SCHEDULER = "cosine"

SAVE_STEPS = 100
LOGGING_STEPS = 10
EVAL_STEPS = 50


# ──────────────────────────────────────────────────────────────────────
# GPU check
# ──────────────────────────────────────────────────────────────────────

def check_gpu():
    if not torch.cuda.is_available():
        print("ERROR: CUDA not available.")
        sys.exit(1)

    gpu = torch.cuda.get_device_properties(0)
    vram_gb = gpu.total_memory / 1e9
    print(f"  GPU: {gpu.name} ({vram_gb:.1f} GB VRAM)")

    if vram_gb < 7:
        print("  WARNING: <7 GB VRAM. Try --max-seq-length 1536 --batch-size 1 --grad-accum 8")
    torch.cuda.empty_cache()


# ──────────────────────────────────────────────────────────────────────
# Model loading
# ──────────────────────────────────────────────────────────────────────

def load_model_and_tokenizer(args):
    print(f"\n  Loading base model: {MODEL_NAME}")
    print("  (FP16 LoRA — 2.3B effective Gemma 4)")

    print("  Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME, trust_remote_code=True
    )
    tokenizer.padding_side = "right"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("  Loading model (FP16, auto device mapping)...")
    print("  (2.3B effective + PLE embeddings — auto GPU/CPU split)")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map={"": "cuda:0"},
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )

    model.eval()
    model.config.use_cache = False

    # Gradient checkpointing
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()

    # Unwrap Gemma4ClippableLinear -> torch.nn.Linear for PEFT compatibility
    try:
        from transformers.models.gemma4.modeling_gemma4 import Gemma4ClippableLinear
        unwrapped = 0
        for name, module in list(model.named_modules()):
            if isinstance(module, Gemma4ClippableLinear) and hasattr(module, "linear"):
                # Replace wrapper with its inner linear layer
                parent = model.get_submodule(".".join(name.split(".")[:-1]) if "." in name else "")
                child_name = name.split(".")[-1]
                setattr(parent if parent else model, child_name, module.linear)
                unwrapped += 1
        print(f"  Unwrapped {unwrapped} x Gemma4ClippableLinear -> Linear")
    except ImportError:
        pass

    # LoRA config
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(model, lora_config)

    model = get_peft_model(model, lora_config)
    trainable, total = model.get_nb_trainable_parameters()
    print(f"  Trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # VRAM log
    allocated = torch.cuda.memory_allocated() / 1e9
    reserved = torch.cuda.memory_reserved() / 1e9
    free = (torch.cuda.get_device_properties(0).total_memory / 1e9) - reserved
    print(f"  VRAM: allocated={allocated:.2f} GB  reserved={reserved:.2f} GB  free={free:.2f} GB")

    return model, tokenizer


# ──────────────────────────────────────────────────────────────────────
# Data loading & formatting
# ──────────────────────────────────────────────────────────────────────

def load_and_format_data(tokenizer, args):
    print(f"\n  Loading: {TRAIN_PATH}")
    dataset = load_dataset("json", data_files={
        "train": str(TRAIN_PATH),
        "validation": str(VAL_PATH),
    })
    print(f"    Train: {len(dataset['train'])}  Val: {len(dataset['validation'])}")

    # Gemma 4 chat template
    # <bos><start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n...<end_of_turn>
    def format_messages(examples):
        texts = []
        for msgs in examples["messages"]:
            text = tokenizer.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=False
            )
            texts.append(text)
        return {"text": texts}

    print("  Applying chat template...")
    dataset = dataset.map(format_messages, batched=True, remove_columns=["messages"])

    # Print token length stats
    lengths = []
    for text in dataset["train"]["text"][:10]:
        tok = tokenizer(text, return_length=True)
        lengths.append(tok["length"][0])
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"    Avg token length (first 10): {avg_len:.0f}  Max seq: {args.max_seq_length}")
    if avg_len > args.max_seq_length:
        print(f"    WARNING: avg length exceeds max_seq_length. Some examples will be truncated.")

    return dataset


# ──────────────────────────────────────────────────────────────────────
# Training callbacks
# ──────────────────────────────────────────────────────────────────────

class LogCallback(TrainerCallback):
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.start_time = time.time()

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and "loss" in logs:
            elapsed = time.time() - self.start_time
            loss = logs.get("loss", float("nan"))
            step = state.global_step
            max_steps = state.max_steps
            pct = step / max_steps * 100 if max_steps else 0
            eta = (elapsed / step * (max_steps - step)) / 60 if step > 0 else 0
            line = (
                f"  step {step}/{max_steps} ({pct:.0f}%) | "
                f"loss={loss:.4f} | elapsed={elapsed/60:.0f}m | ETA={eta:.0f}m"
            )
            print(line)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"{step},{loss},{elapsed}\n")


# ──────────────────────────────────────────────────────────────────────
# Train
# ──────────────────────────────────────────────────────────────────────

def train(model, tokenizer, dataset, args):
    steps_per_epoch = math.ceil(len(dataset["train"]) / (args.batch_size * args.grad_accum))
    total_steps = steps_per_epoch * args.epochs

    print(f"\n  Training config:")
    print(f"    Examples: {len(dataset['train'])} train / {len(dataset['validation'])} val")
    print(f"    Steps/epoch: {steps_per_epoch}   Total: {total_steps} ({args.epochs} epochs)")
    print(f"    Batch: {args.batch_size} x {args.grad_accum} accumulation = {args.batch_size * args.grad_accum} effective")
    print(f"    LR: {LEARNING_RATE}  LoRA r={args.lora_r} alpha={LORA_ALPHA}")
    print(f"    Max seq length: {args.max_seq_length}")

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=args.grad_accum,
        num_train_epochs=args.epochs,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type=LR_SCHEDULER,
        warmup_steps=10,
        fp16=True,                              # mixed precision for FP16 model
        bf16=False,
        logging_steps=LOGGING_STEPS,
        eval_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        optim="adamw_torch",                    # standard AdamW for FP16 model
        report_to="none",
        dataloader_num_workers=0,
        remove_unused_columns=False,
        max_grad_norm=1.0,
        ddp_find_unused_parameters=False,
        gradient_checkpointing=True,            # save VRAM by recomputing activations
    )

    if args.test:
        training_args.max_steps = 50
        training_args.save_strategy = "no"
        training_args.load_best_model_at_end = False
        training_args.eval_steps = 25
        training_args.logging_steps = 5

    if args.resume:
        training_args.resume_from_checkpoint = args.resume

    log_path = OUTPUT_DIR / "training.log"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w") as f:
        f.write("step,loss,elapsed_seconds\n")

    print("  Tokenizing dataset...")
    def tokenize_fn(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=args.max_seq_length,
            padding=False,
        )
    dataset = dataset.map(
        tokenize_fn, batched=True, remove_columns=["text"],
        desc="Tokenizing",
    )
    print(f"    Done. Avg token length: {sum(len(d['input_ids']) for d in dataset['train'].select(range(10))) / 10:.0f}")

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,           # causal LM, not masked
        pad_to_multiple_of=8,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        data_collator=data_collator,
        callbacks=[LogCallback(log_path)],
    )

    print(f"\n  Starting training ({total_steps} steps)...")
    print(f"  Checkpoints: {OUTPUT_DIR}")
    print()

    trainer.train(resume_from_checkpoint=args.resume)

    if not test_mode:
        print(f"\n  Saving LoRA adapter to {OUTPUT_DIR}")
        model.save_pretrained(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)
        print(f"  Done.")

    return trainer


# ──────────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────────

def print_summary(trainer):
    print(f"\n{'='*60}")
    print(f"  TRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"\n  LoRA adapter saved to: {OUTPUT_DIR}")
    print(f"\n  Next steps:")
    print(f"    1. Merge LoRA with base model:")
    print(f"       python scripts/merge_lora.py")
    print(f"    2. Convert to GGUF for Ollama:")
    print(f"       python scripts/convert_to_gguf.py")
    print(f"    3. Import into Ollama:")
    print(f"       ollama create caforb-v1 -f Modelfile")


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="LoRA fine-tune Gemma 4 12B QAT on CaForB.")
    parser.add_argument("--test", action="store_true", help="Quick test (50 steps, no save)")
    parser.add_argument("--epochs", type=int, default=NUM_EPOCHS)
    parser.add_argument("--max-seq-length", type=int, default=MAX_SEQ_LENGTH)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--grad-accum", type=int, default=GRAD_ACCUM)
    parser.add_argument("--resume", type=str, default=None, help="Resume from checkpoint path")
    parser.add_argument("--lora-r", type=int, default=LORA_R)
    args = parser.parse_args()

    print("=" * 60)
    print("  CaForB: LoRA Fine-Tuning")
    print("=" * 60)
    print(f"  Base model: {MODEL_NAME}")

    check_gpu()

    if not TRAIN_PATH.exists():
        print(f"ERROR: {TRAIN_PATH} not found. Run convert_to_jsonl.py first.")
        sys.exit(1)

    model, tokenizer = load_model_and_tokenizer(args)
    dataset = load_and_format_data(tokenizer, args)
    trainer = train(model, tokenizer, dataset, args)

    if not args.test:
        print_summary(trainer)


if __name__ == "__main__":
    main()
