#!/bin/bash
# export_all.sh — Merge the trained LoRA adapter and export a quantized GGUF.
#
# Run on the cloud GPU AFTER `bash cloud_train.sh` finishes.
# Outputs caforb-v1.Q4_K_M.gguf — download that single file to your machine.
#
# Disk: needs a >=100GB container disk (see CLOUD_GUIDE.md).

set -e

echo "============================================"
echo "  CaForB — Merge LoRA + Export GGUF"
echo "============================================"

python scripts/merge_lora.py
python scripts/export_gguf.py

echo ""
echo "============================================"
echo "  Export complete: caforb-v1.Q4_K_M.gguf"
echo ""
echo "  Download it to your Windows machine, then:"
echo "    ollama create caforb-v1 -f Modelfile"
echo "============================================"
