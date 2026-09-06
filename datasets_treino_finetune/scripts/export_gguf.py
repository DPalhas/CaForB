#!/usr/bin/env python3
"""
export_gguf.py — Convert the merged fp16 model to a quantized GGUF for Ollama.

Runs on the cloud GPU. Orchestrates llama.cpp:

    1. Clones llama.cpp (shallow) if not already present.
    2. Builds `llama-quantize` (small CPU-only binary, fast).
    3. Converts merged-model/ -> caforb-v1-f16.gguf (f16).
    4. Quantizes -> caforb-v1.Q4_K_M.gguf (matches the runtime `gemma4:12B`).
    5. Deletes intermediates to free disk.

Usage:
    python scripts/export_gguf.py                                # defaults below
    python scripts/export_gguf.py --model-dir merged-model \
                                  --out caforb-v1.Q4_K_M.gguf \
                                  --quant Q4_K_M

Disk (use a >=100GB container disk):
    base cache ~24GB + merged ~24GB + f16 gguf ~24GB + final Q4 ~8GB.
    Intermediates are removed as we go, so peak is ~72GB.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LLAMA_CPP_URL = "https://github.com/gggerganov/llama.cpp.git"

DEFAULT_MODEL_DIR = BASE_DIR / "merged-model"
DEFAULT_OUT = BASE_DIR / "caforb-v1.Q4_K_M.gguf"
DEFAULT_LLAMA_CPP = BASE_DIR / "llama.cpp"


def run(cmd, cwd=None, check=True):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, cwd=cwd, check=check)


def clone_llama_cpp(dest: Path) -> Path:
    if (dest / "convert_hf_to_gguf.py").exists():
        print(f"  llama.cpp already present: {dest}")
        return dest
    print(f"  Cloning llama.cpp -> {dest}")
    run(["git", "clone", "--depth", "1", LLAMA_CPP_URL, str(dest)])
    return dest


def build_quantize(llama_cpp: Path) -> Path:
    quantize = llama_cpp / "llama-quantize"
    if quantize.exists():
        print(f"  llama-quantize already built: {quantize}")
        return quantize
    print("  Building llama-quantize (CPU-only, ~2-3 min)...")
    run(["make", "llama-quantize", "-j"], cwd=llama_cpp)
    if not quantize.exists():
        print("ERROR: llama-quantize build failed.")
        raise SystemExit(1)
    return quantize


def ensure_convert_deps():
    """convert_hf_to_gguf.py needs the `gguf` and `sentencepiece` packages."""
    missing = []
    for mod in ("gguf", "sentencepiece"):
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"  Installing missing conversion deps: {', '.join(missing)}")
        run([sys.executable, "-m", "pip", "install", "-q", *missing])


def main():
    parser = argparse.ArgumentParser(description="Export merged model to quantized GGUF.")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR,
                        help="Merged fp16 HF model directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="Final quantized GGUF path")
    parser.add_argument("--quant", default="Q4_K_M", help="Quantization type")
    parser.add_argument("--llama-cpp", type=Path, default=DEFAULT_LLAMA_CPP,
                        help="llama.cpp directory (cloned if missing)")
    parser.add_argument("--keep-intermediates", action="store_true",
                        help="Keep the f16 GGUF and merged-model dir")
    args = parser.parse_args()

    if not args.model_dir.exists():
        print(f"ERROR: model dir not found: {args.model_dir}")
        print("Run `python scripts/merge_lora.py` first.")
        raise SystemExit(1)

    f16_gguf = args.out.with_suffix(".f16.gguf")

    llama_cpp = clone_llama_cpp(args.llama_cpp)
    quantize = build_quantize(llama_cpp)
    ensure_convert_deps()

    print(f"\n  Converting {args.model_dir} -> {f16_gguf} (f16)")
    run([
        sys.executable, str(llama_cpp / "convert_hf_to_gguf.py"),
        str(args.model_dir),
        "--outfile", str(f16_gguf),
        "--outtype", "f16",
    ], cwd=llama_cpp)

    print(f"\n  Quantizing {f16_gguf} -> {args.out} ({args.quant})")
    run([str(quantize), str(f16_gguf), str(args.out), args.quant])

    if not args.keep_intermediates:
        print("\n  Cleaning up intermediates...")
        for p in (f16_gguf, args.model_dir):
            if p.exists():
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                print(f"    removed {p}")

    print(f"\n  Done. Final GGUF: {args.out}")
    print(f"  Download it to your Windows machine and run:")
    print(f"    ollama create caforb-v1 -f Modelfile")


if __name__ == "__main__":
    main()
