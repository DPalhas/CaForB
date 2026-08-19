#!/usr/bin/env python3
"""
convert_to_jsonl.py — Phase 4: Convert individual training examples to instruction-fine-tuning JSONL.

Splits 80/20 train/validation, shuffles, and outputs JSONL files compatible with
HuggingFace datasets, Unsloth, and Ollama import.

Outputs:
    final/train.jsonl          — 400 examples (shuffled)
    final/validation.jsonl     — 104 examples (shuffled)
    final/coverage_report.json — Distribution breakdown per split

Usage:
    python scripts/convert_to_jsonl.py
    python scripts/convert_to_jsonl.py --split 80 20
    python scripts/convert_to_jsonl.py --seed 42
"""

import json
import random
import argparse
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

# Make the CaForB app importable so training mirrors the runtime prompts exactly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.services.llm_services import (  # noqa: E402
    build_first_system_prompt,
    build_reassessment_system_prompt,
    _format_company_data,
)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw"
FINAL_DIR = BASE_DIR / "final"

# ──────────────────────────────────────────────────────────────────────
# Load and validate
# ──────────────────────────────────────────────────────────────────────

def load_all_examples() -> list[dict]:
    examples = []
    for fp in sorted(RAW_DIR.glob("*.json")):
        try:
            d = json.loads(fp.read_text(encoding="utf-8"))
            if "input" in d and "output" in d:
                examples.append(d)
        except (json.JSONDecodeError, KeyError):
            continue
    return examples


# ──────────────────────────────────────────────────────────────────────
# Format assistant output
# ──────────────────────────────────────────────────────────────────────

def format_assistant_output(ex: dict) -> str:
    out = ex["output"]
    return json.dumps(out, ensure_ascii=False)


# ──────────────────────────────────────────────────────────────────────
# Convert to JSONL
# ──────────────────────────────────────────────────────────────────────

def build_reassessment_user(ex: dict) -> str:
    """User message for reassessment: simple prior block + current data."""
    inp = ex["input"]
    company = inp["company"]
    answers = inp["answers"]

    prev = inp.get("previous_assessment", {})
    pf = prev.get("fields", prev) if isinstance(prev, dict) else {}
    prior_lines = ["--- PRIOR ASSESSMENT ---"]
    prior_lines.append(f"Company: {pf.get('companyName', '?')}")
    prior_lines.append(f"Sector: {pf.get('sector', '?')}")
    prior_lines.append(
        f"Risk: {pf.get('riskAppetite', '?')} | "
        f"Priority: {pf.get('strategicPriority', '?')}"
    )
    prior_lines.append(
        f"Regulatory: {pf.get('regulatoryEnvironment', '?')} | "
        f"Competition: {pf.get('competitivePressure', '?')}"
    )
    prior_lines.append(
        f"Budget: {pf.get('budgetPercentage', '?')}% of "
        f"{pf.get('revenueRange', '?')}"
    )
    if pf.get('mainBarrier'):
        prior_lines.append(f"Barriers: {', '.join(pf.get('mainBarrier', []))}")
    prior_lines.append("")
    prior_lines.append(
        f"Changes since last assessment: {inp.get('changes_since_last', 'N/A')}"
    )
    prior_lines.append(
        f"Recommendation status: {json.dumps(inp.get('recommendation_status', {}))}"
    )

    prior_block = "\n".join(prior_lines)
    data_block = _format_company_data(company, answers)
    return f"{prior_block}\n\nCURRENT ASSESSMENT:\n{data_block}"


def convert(examples: list[dict]) -> list[dict]:
    records = []
    for ex in examples:
        is_reassess = ex.get("assessment_type") == "reassessment"
        inp = ex["input"]
        company = inp.get("company", {})
        answers = inp.get("answers", {})

        system = (
            build_reassessment_system_prompt(answers)
            if is_reassess
            else build_first_system_prompt(answers)
        )
        user = (
            build_reassessment_user(ex)
            if is_reassess
            else _format_company_data(company, answers)
        )
        record = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": format_assistant_output(ex)},
            ]
        }
        records.append(record)
    return records


# ──────────────────────────────────────────────────────────────────────
# Coverage report
# ──────────────────────────────────────────────────────────────────────

def build_coverage_report(train: list[dict], val: list[dict]) -> dict:
    def tally(records: list[dict]) -> dict:
        counts = Counter()
        sectors = Counter()
        sizes = Counter()
        risks = Counter()

        for r in records:
            # Parse the original id from the user content
            user_text = r["messages"][1]["content"]
            sector_match = re.search(r"Sector: (.+)", user_text)
            size_match = re.search(r"Size: (.+)", user_text)
            risk_match = re.search(r"Risk Appetite: (.+)", user_text)

            if sector_match: sectors[sector_match.group(1)] += 1
            if size_match: sizes[size_match.group(1)] += 1
            if risk_match: risks[risk_match.group(1)] += 1

        return {
            "sectors": dict(sectors),
            "sizes": dict(sizes),
            "risks": dict(risks),
        }

    return {
        "train_count": len(train),
        "validation_count": len(val),
        "train": tally(train),
        "validation": tally(val),
    }


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Convert training examples to JSONL.")
    parser.add_argument("--split", type=int, nargs=2, default=[80, 20],
                        help="Train/validation split percentages (default: 80 20)")
    parser.add_argument("--seed", type=int, default=42, help="Shuffle seed (default: 42)")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    args = parser.parse_args()

    train_pct, val_pct = args.split
    if train_pct + val_pct != 100:
        print("Error: split percentages must sum to 100")
        return

    output_dir = Path(args.output_dir) if args.output_dir else FINAL_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading examples...")
    examples = load_all_examples()
    print(f"  Loaded {len(examples)} examples")

    print("Converting to instruction format...")
    records = convert(examples)

    print("Shuffling...")
    random.seed(args.seed)
    random.shuffle(records)

    split_idx = int(len(records) * train_pct / 100)
    train = records[:split_idx]
    validation = records[split_idx:]

    train_path = output_dir / "train.jsonl"
    val_path = output_dir / "validation.jsonl"

    for path, data in [(train_path, train), (val_path, validation)]:
        with open(path, "w", encoding="utf-8") as f:
            for record in data:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"  {path.name}: {len(data)} records ({path.stat().st_size / 1024 / 1024:.1f} MB)")

    print("\nBuilding coverage report...")
    report = build_coverage_report(train, validation)
    report_path = output_dir / "coverage_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  Coverage report: {report_path.name}")
    print(f"\n  Train split:")
    print(f"    {report['train_count']} examples")
    print(f"    Sectors: {len(report['train']['sectors'])} unique")
    print(f"    Sizes: {report['train']['sizes']}")
    print(f"    Risks: {report['train']['risks']}")
    print(f"\n  Validation split:")
    print(f"    {report['validation_count']} examples")
    print(f"    Sectors: {len(report['validation']['sectors'])} unique")
    print(f"    Sizes: {report['validation']['sizes']}")
    print(f"    Risks: {report['validation']['risks']}")
    print(f"\n  Done.")


if __name__ == "__main__":
    main()
