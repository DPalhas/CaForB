#!/bin/bash
# cloud_train.sh — Fine-tune Gemma 4 12B on RunPod / Lambda Labs
#
# Recommended GPU: RTX 4090 (24GB) — $0.69/hr on RunPod
# Training time: ~6-10 hours  |  Cost: ~$4-7
#
# Usage:
#   1. Upload caforb_cloud.zip to your cloud instance
#   2. unzip caforb_cloud.zip
#   3. bash cloud_train.sh

set -e

echo "============================================"
echo "  CaForB — 12B Gemma 4 Fine-Tuning"
echo "  Target: google/gemma-4-12B-it"
echo "  VRAM: ~14-18 GB (fits in 24GB)"
echo "============================================"

# GPU check
echo ""
echo "1. GPU Check"
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader 2>/dev/null || echo "WARNING: No GPU detected"
echo ""

# Install deps
echo "2. Installing dependencies..."
pip install -q -r requirements_cloud.txt
echo "   Done."
echo ""

# Verify dataset
echo "3. Verifying dataset..."
if [ ! -f "final/train.jsonl" ]; then
    echo "ERROR: final/train.jsonl not found."
    echo "Upload your dataset first: caforb_cloud.zip should contain final/train.jsonl"
    exit 1
fi
echo "   Train: $(wc -l < final/train.jsonl) records"
echo "   Val:   $(wc -l < final/validation.jsonl) records"
echo ""

# Quick connectivity test (skip if model not yet public)
echo "4. Checking HF connectivity..."
python3 -c "from huggingface_hub import list_models; print('   OK')" 2>/dev/null || echo "   (huggingface_hub not installed, skipping)"
echo ""

# Training
echo "5. Starting training..."
echo "   Config: 4-bit QLoRA, r=8, max_seq=4096, 3 epochs"
echo "   ETA: ~6-10 hours"
echo ""

python scripts/train_caforb.py \
    --model google/gemma-4-12B-it \
    --max-seq-length 4096 \
    --lora-r 8 \
    --epochs 3

echo ""
echo "============================================"
echo "  Training complete!"
echo ""
echo "  Download caforb-lora/ to your machine:"
echo "    RunPod: File browser → download caforb-lora/"
echo "    Lambda: scp -r user@ip:~/caforb-lora/ ."
echo ""
echo "  Then merge with base model to create caforb-v1."
echo "============================================"
