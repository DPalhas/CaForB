#!/usr/bin/env python3
"""
setup_ml.py — Install all dependencies for QLoRA fine-tuning on Windows.

Run once before train_caforb.py:
    python scripts/setup_ml.py
"""

import subprocess
import sys

packages = [
    "torch --index-url https://download.pytorch.org/whl/cu126",
    "transformers>=4.46",
    "peft",
    "trl",
    "accelerate",
    "datasets",
    "bitsandbytes-windows",  # Windows port of bitsandbytes
    "xformers",              # memory-efficient attention (optional)
    "wandb",                 # optional logging
]


def run(cmd: str) -> bool:
    parts = cmd.split()
    print(f"\n  Installing: {' '.join(parts[:3])}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install"] + parts,
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"  WARNING: {result.stderr[-200:]}")
        return False
    print(f"  OK")
    return True


def main():
    print("Installing ML dependencies for CaForB fine-tuning...")
    for pkg in packages:
        run(pkg)
    print("\nDone. Run train_caforb.py to start fine-tuning.")


if __name__ == "__main__":
    main()
