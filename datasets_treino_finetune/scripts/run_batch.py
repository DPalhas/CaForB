#!/usr/bin/env python3
"""
run_batch.py — Batch orchestration for generating validated training examples.

Wraps generate_one.py for efficient batch processing with:
  - Progress tracking and ETA
  - Automatic skip of already-generated files
  - Batch summary with success/skip/fail counts
  - Dry-run mode to preview
  - Retry-failed mode for incomplete examples

Usage:
    python scripts/run_batch.py --start 0 --end 49
    python scripts/run_batch.py --start 50 --end 99 --model gemma4:e2b-it-qat --gpu-layers -1
    python scripts/run_batch.py --retry-failed     # retries all missing indices
    python scripts/run_batch.py --start 0 --end 503 # full run (all 504)
"""

import sys
import time
from pathlib import Path

# Import directly from generate_one — no subprocess overhead
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_one import generate_one, load_survey, OUTPUT_DIR, INPUT_PATH


def count_existing(indices: list[int]) -> int:
    count = 0
    for i in indices:
        survey = load_survey(i)
        out_path = OUTPUT_DIR / f"{survey['id']}.json"
        if out_path.exists():
            count += 1
    return count


def find_missing_indices(total: int = 504) -> list[int]:
    missing = []
    for i in range(total):
        survey = load_survey(i)
        out_path = OUTPUT_DIR / f"{survey['id']}.json"
        if not out_path.exists():
            missing.append(i)
    return missing


def run_batch(
    indices: list[int],
    model: str,
    gpu_layers: int,
    num_predict: int,
    max_retries: int,
) -> dict:
    total = len(indices)
    already = count_existing(indices)
    todo = total - already

    if already:
        print(f"  Already exist: {already}/{total}  (skipping)")

    if todo == 0:
        print("  All complete. Nothing to do.")
        return {"success": 0, "skip": already, "fail": 0}

    print(f"  Remaining: {todo}")
    print()

    results = {"success": 0, "skip": already, "fail": 0}
    start_time = time.time()

    for seq, i in enumerate(indices, 1):
        survey = load_survey(i)
        ex_id = survey["id"]
        out_path = OUTPUT_DIR / f"{ex_id}.json"

        if out_path.exists():
            continue

        combo = survey["combo_id"]
        elapsed = time.time() - start_time
        rate_ok = results["success"] / elapsed * 60 if elapsed > 0 and results["success"] > 0 else 0
        remaining = todo - results["success"] - results["fail"]
        eta = remaining / max(rate_ok, 0.1) if rate_ok > 0 else 0

        print(
            f"  [{seq}/{total}] {ex_id}  {combo}  "
            f"OK:{results['success']:>3}  FAIL:{results['fail']:>2}  "
            f"ETA:{eta:>4.0f}m",
            flush=True,
        )

        result_id = generate_one(i, model, gpu_layers, num_predict, max_retries)

        if result_id:
            results["success"] += 1
        elif out_path.exists():
            results["skip"] += 1
        else:
            results["fail"] += 1

        print()  # newline after generate_one's output

    elapsed = time.time() - start_time
    rate = results["success"] / elapsed * 60 if elapsed > 0 else 0

    print(f"\n{'=' * 60}")
    print(
        f"  Batch complete: {results['success']} ok, "
        f"{results['skip']} skip, {results['fail']} fail"
    )
    print(f"  Time: {elapsed:.0f}s  |  Rate: {rate:.1f} ex/min")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Batch generation of validated training examples.")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    parser.add_argument("--end", type=int, default=503, help="End index (inclusive)")
    parser.add_argument("--model", default="gemma4:e2b-it-qat", help="Ollama model name")
    parser.add_argument("--gpu-layers", type=int, default=-1, help="GPU layers (-1=all, 0=CPU)")
    parser.add_argument("--num-predict", type=int, default=12288, help="Max output tokens")
    parser.add_argument("--retries", type=int, default=5, help="Max retry attempts")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't generate")
    parser.add_argument("--retry-failed", action="store_true", help="Retry all missing indices")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        import json
        data = json.load(f)
    total_available = len(data)

    if args.retry_failed:
        indices = find_missing_indices(total_available)
        if not indices:
            print("All 504 examples present. Nothing to retry.")
            return
        print(f"Retry mode: {len(indices)} missing example(s)")
    elif args.start > args.end:
        print("Error: --start must be <= --end")
        sys.exit(1)
    else:
        indices = list(range(args.start, min(args.end, total_available - 1) + 1))

    if args.dry_run:
        existing = count_existing(indices)
        todo = len(indices) - existing
        print(f"Dry run: {len(indices)} total, {existing} exist, {todo} would be generated")
        return

    if args.retry_failed and len(indices) <= 10:
        print(f"\nMissing indices: {indices}\n")

    print(f"Model: {args.model}")
    print(f"Device: {'GPU' if args.gpu_layers != 0 else 'CPU'}")
    print(f"Tokens: {args.num_predict}  |  Max retries: {args.retries}")
    print(f"Indices: {args.start}–{min(args.end, total_available - 1)} ({len(indices)} examples)")
    print()

    run_batch(indices, args.model, args.gpu_layers, args.num_predict, args.retries)


if __name__ == "__main__":
    main()
