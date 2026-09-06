# Cloud Fine-Tuning Guide — Gemma 4 12B

## Overview

Fine-tune `google/gemma-4-12B-it` (full 12B Gemma 4) using 4-bit QLoRA,
then merge the adapter and export a quantized GGUF for Ollama.

The full training takes ~2-3 hours at ~$3-5 on an A100 (80GB).

**Why 12B instead of 2.3B E2B:** The 12B model produces noticeably better reassessments —
coherent carry_forward, realistic progress tracking, budget-anchored recommendations —
and can generate the full extended contract in one call instead of two phases.

## Step 1 — Pack your files

From your `datasets_treino_finetune/` directory, the zip `caforb_cloud.zip` already
contains everything needed:

```
datasets_treino_finetune/
├── final/
│   ├── train.jsonl          (733 records)
│   └── validation.jsonl     (184 records)
├── scripts/
│   ├── train_caforb.py      (training script)
│   ├── merge_lora.py        (merge adapter -> fp16 model)
│   ├── export_gguf.py       (llama.cpp convert + quantize)
│   ├── export_all.sh        (one-command merge + export)
│   └── import_to_ollama.ps1 (Windows-side import)
├── cloud_train.sh           (one-click launcher)
├── Modelfile                (Ollama import template)
└── requirements_cloud.txt   (pip deps)
```

## Step 2 — Deploy a GPU

1. Go to https://runpod.io → **Pods** → **Deploy**
2. Template: **RunPod PyTorch 2.6** (or latest)
3. GPU: **A100 SXM** (80 GB, ~$1.39/hr)
4. **Container disk: 100 GB** (needed for base model + merge + GGUF; see disk note below)
5. **Start Jupyter notebook** ✓ and **SSH terminal access** ✓
6. Deploy, wait ~30s for "Running"

## Step 3 — Upload and train

Upload `caforb_cloud.zip` (Jupyter file browser → drag-and-drop), then in a terminal:

```bash
unzip caforb_cloud.zip
bash cloud_train.sh
```

Optional smoke test first (~5 min, catches env problems cheaply):

```bash
pip install -r requirements_cloud.txt
python scripts/train_caforb.py --test
```

Watch for: model downloads without a 404, GPU detected, loss trending down.
If you see loss go to `nan`/`inf`, stop and re-check.

## Step 4 — Merge + export to GGUF (on the pod)

**Do this on the pod, before stopping it** — the Windows machine has neither the
GPU nor torch/transformers/peft installed. The merge needs ~24 GB fp16 VRAM.

```bash
bash scripts/export_all.sh
```

This:
1. Merges the LoRA adapter into the base model (→ `merged-model/`, fp16)
2. Clones + builds llama.cpp's `llama-quantize`
3. Converts to f16 GGUF, then quantizes to **Q4_K_M** (matches runtime `gemma4:12B`)
4. Deletes intermediates to free disk

Output: `caforb-v1.Q4_K_M.gguf` (~8 GB).

**Troubleshooting:** if `convert_hf_to_gguf.py` errors on the architecture, the
cloned llama.cpp is too old to support Gemma 4 — re-clone latest master.

## Step 5 — Download the GGUF

From the Jupyter file browser, right-click `caforb-v1.Q4_K_M.gguf` → **Download**,
then **stop** the pod (billing stops).

Place it at:
```
C:\Users\david\OneDrive\Ambiente de Trabalho\MIG\Dissertação\CaForB\datasets_treino_finetune\caforb-v1.Q4_K_M.gguf
```

## Step 6 — Import into Ollama (Windows)

With Ollama running:

```powershell
cd C:\Users\david\OneDrive\Ambiente de Trabalho\MIG\Dissertação\CaForB\datasets_treino_finetune
powershell -ExecutionPolicy Bypass -File scripts\import_to_ollama.ps1
```

Or manually:

```powershell
ollama create caforb-v1 -f Modelfile
ollama run caforb-v1 "Reply with exactly: OK"
```

## Step 7 — Point the app at the new model

In `core/services/llm_services.py`, change:

```python
DEFAULT_MODEL = "gemma4:12B"   # -> "caforb-v1"
```

Also update the `"gemma4:12B"` fallback in `core/schema.py`. Then run the backend,
submit a fresh assessment and a reassessment, and verify the JSON parses and renders.

## Disk sizing

The export step needs ~72 GB at peak (base cache 24 + merged 24 + f16 GGUF 24),
so use a **100 GB container disk**. Intermediates are auto-deleted as export
progresses, ending at ~32 GB (base cache + final Q4 GGUF).

## Cost estimate

| Service | GPU | Price/hr | Training time | Total cost |
|---|---|---|---|---|
| RunPod | A100 SXM (80GB) | $1.39 | ~2-3 hours | ~$3-5 |

## Alternate model

If `google/gemma-4-12B-it` is not available on HuggingFace yet, change the model:
```bash
python scripts/train_caforb.py --model google/gemma-4-12B-it  # try this
# or any other HuggingFace model ID
```
Check https://huggingface.co/google for the latest Gemma 4 models.

## Troubleshooting

- **OOM**: Lower `--max-seq-length` in cloud_train.sh (try 4096)
- **Model not found**: RunPod might need `huggingface-cli login` if the model is gated
- **Slow downloads**: The base model is ~24 GB (fp16) — first download may take several minutes
- **GGUF conversion fails on arch**: llama.cpp too old — re-clone latest master for Gemma 4 support
