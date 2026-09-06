#!/usr/bin/env python3
"""
merge_lora.py — Merge the trained LoRA adapter back into the full base model.

Runs on the cloud GPU (A100 80GB), where torch/transformers/peft are already
installed. Produces a full fp16 model under `merged-model/`, ready for GGUF
conversion by `export_gguf.py`.

Usage:
    python scripts/merge_lora.py                        # defaults below
    python scripts/merge_lora.py --base google/gemma-4-12B-it \
                                 --adapter caforb-lora \
                                 --out merged-model

Notes:
    - Loads the base in fp16 (not 4-bit): merging a QLoRA adapter over a 4-bit
      base yields a 4-bit model, which is unsuitable for GGUF conversion.
    - ~24 GB VRAM for the fp16 12B model (fits in 80GB A100).
"""

import argparse
import re
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BASE = "google/gemma-4-12B-it"
DEFAULT_ADAPTER = BASE_DIR / "caforb-lora"
DEFAULT_OUT = BASE_DIR / "merged-model"


def resolve_adapter(adapter: Path) -> Path:
    """Pick the adapter dir to load.

    The Trainer saves the final adapter via save_pretrained (root has
    adapter_config.json), but on a crash only the periodic checkpoint-*
    dirs survive. If the root has no adapter, fall back to the
    highest-numbered checkpoint.
    """
    if (adapter / "adapter_config.json").exists():
        return adapter
    checkpoints = sorted(
        (p for p in adapter.glob("checkpoint-*") if (p / "adapter_config.json").exists()),
        key=lambda p: int(re.search(r"checkpoint-(\d+)$", p.name).group(1)),
    )
    if not checkpoints:
        print(f"ERROR: no adapter_config.json found in {adapter} or its checkpoints.")
        raise SystemExit(1)
    chosen = checkpoints[-1]
    print(f"  No adapter at {adapter}; using latest checkpoint: {chosen}")
    return chosen


def main():
    parser = argparse.ArgumentParser(description="Merge LoRA adapter into base model.")
    parser.add_argument("--base", default=DEFAULT_BASE, help="HF base model ID")
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER,
                        help="Path to the LoRA adapter directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="Output directory for the merged fp16 model")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("ERROR: CUDA not available — merging needs the GPU.")
        raise SystemExit(1)

    adapter = resolve_adapter(args.adapter)

    print(f"\n  Loading base model (fp16): {args.base}")
    model = AutoModelForCausalLM.from_pretrained(
        args.base,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"  Loading LoRA adapter: {adapter}")
    model = PeftModel.from_pretrained(model, str(adapter))

    print("  Merging adapter into base weights...")
    model = model.merge_and_unload()

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"  Saving merged model to: {args.out}")
    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)

    print("\n  Merge complete.")
    print(f"  Next: python scripts/export_gguf.py --model-dir {args.out}")


if __name__ == "__main__":
    main()
