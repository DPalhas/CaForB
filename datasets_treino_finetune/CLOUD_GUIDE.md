# Cloud Fine-Tuning Guide — Gemma 4 12B

## Overview

Fine-tune `google/gemma-4-12b-it` (full 12B Gemma 4) using 4-bit QLoRA.
The full training takes ~6-10 hours at ~$4-7 on an RTX 4090.

**Why 12B instead of 2.3B E2B:** The 12B model produces noticeably better reassessments —
coherent carry_forward, realistic progress tracking, budget-anchored recommendations —
and can generate the full extended contract in one call instead of two phases.

## Step 1 — Pack your files

From your `datasets_treino_finetune/` directory, upload these to the cloud instance:

```
datasets_treino_finetune/
├── final/
│   ├── train.jsonl          (733 records, 5.7 MB)
│   └── validation.jsonl     (184 records, 1.5 MB)
├── scripts/
│   └── train_caforb.py      (training script)
├── cloud_train.sh           (one-click launcher)
└── requirements_cloud.txt   (pip deps)
```

**Create a zip file to upload:**
```powershell
cd C:\Users\david\OneDrive\Ambiente de Trabalho\MIG\Dissertação\CaForB\datasets_treino_finetune
Compress-Archive -Path final,scripts\train_caforb.py,cloud_train.sh,requirements_cloud.txt -DestinationPath caforb_cloud.zip
```

## Step 2 — Deploy a GPU (choose one)

### Option A: RunPod (easiest, $0.69/hr for RTX 4090)

1. Go to https://runpod.io → sign up (add ~$10 credit)
2. Click **Pods** → **Deploy**
3. Choose template: **RunPod Pytorch 2.6** (or latest)
4. GPU: **RTX 4090** (24 GB VRAM, $0.69/hr)
5. Click **Deploy**
6. Wait for pod to start (~30 sec), then click **Connect** → **Web Terminal**

### Option B: Lambda Labs ($0.50/hr)

1. Go to https://lambdalabs.com/service/gpu-cloud
2. Deploy a **1x RTX 4090** instance
3. SSH in

## Step 3 — Upload and run

In the cloud terminal:

```bash
# Upload your zip (from RunPod Jupyter, use the file upload button;
# from Lambda, use scp or rsync)

# If you zipped the files:
unzip caforb_cloud.zip

# Make sure the directory structure matches:
# ./final/train.jsonl
# ./final/validation.jsonl
# ./scripts/train_caforb.py
# ./cloud_train.sh
# ./requirements_cloud.txt

# Run training
chmod +x cloud_train.sh
bash cloud_train.sh
```

## Step 4 — Download the model

After training finishes, download `caforb-lora/` back to your machine:

```powershell
# From RunPod: use the file browser to download caforb-lora/ as a zip
# From Lambda: scp -r user@ip:~/caforb-lora/ .
```

Place the downloaded folder at:
```
C:\Users\david\OneDrive\Ambiente de Trabalho\MIG\Dissertação\CaForB\datasets_treino_finetune\caforb-lora\
```

## Step 5 — Merge and import to Ollama

```powershell
# On your Windows machine, in the datasets_treino_finetune/ dir:

# 1. Merge LoRA into base model
python scripts/merge_lora.py

# 2. Convert to GGUF
python scripts/convert_to_gguf.py caforb-lora/ caforb-v1.Q4_K_M.gguf

# 3. Import to Ollama
echo "FROM caforb-v1.Q4_K_M.gguf" > Modelfile
ollama create caforb-v1 -f Modelfile

# 4. Test
ollama run caforb-v1
```

## Cost estimate

| Service | GPU | Price/hr | Training time | Total cost |
|---|---|---|---|---|
| RunPod | RTX 4090 | $0.69 | ~6-10 hours | ~$4-7 |
| Lambda Labs | RTX 4090 | $0.50 | ~6-10 hours | ~$3-5 |

With RunPod's $10 minimum preload, you'll have $3-6 leftover for hyperparameter tuning or model hosting.

## Alternate model

If `google/gemma-4-12b-it` is not available on HuggingFace yet, change the model:
```bash
python scripts/train_caforb.py --model google/gemma-4-12b-it  # try this
# or any other HuggingFace model ID
```
Check https://huggingface.co/google for the latest Gemma 4 models.

## Troubleshooting

- **OOM**: Lower `--max-seq-length` in cloud_train.sh (try 2048)
- **Model not found**: RunPod might need `huggingface-cli login` if model is gated
- **Slow downloads**: The base model `google/gemma-4-E2B-it` is ~5 GB — first download may take a few minutes
