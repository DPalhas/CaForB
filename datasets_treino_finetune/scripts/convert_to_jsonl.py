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
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw"
FINAL_DIR = BASE_DIR / "final"

REVENUE_RANGE_MIDPOINTS = {
    "under_1m": 500_000,
    "1m_to_10m": 5_500_000,
    "10m_to_50m": 30_000_000,
    "over_50m": 75_000_000,
}

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
# Format user input (mirrors build_innovation_prompt from llm_services.py)
# ──────────────────────────────────────────────────────────────────────

def compute_budget(answers: dict) -> str:
    pct = answers.get("budgetPercentage")
    revenue_key = answers.get("revenueRange")
    if pct is None or not revenue_key:
        return "unknown"
    midpoint = REVENUE_RANGE_MIDPOINTS.get(revenue_key)
    if midpoint is None:
        return f"{pct}% of revenue"
    amount = int(midpoint * (pct / 100))
    return f"~EUR{amount:,}/year ({pct}% of revenue)"


def format_user_input(ex: dict) -> str:
    inp = ex["input"]
    company = inp["company"]
    answers = inp["answers"]
    budget = compute_budget(answers)

    lines = [
        f"Company: {company.get('name', 'Unknown')}",
        f"Sector: {company.get('sector', 'Unknown')}",
        f"Size: {company.get('size', 'Unknown')}",
        f"",
        f"Company Description: {answers.get('companyDescription', 'Not provided')}",
        f"",
        f"Innovation Process: {answers.get('innovationProcess', 'unknown')}",
        f"Digital Maturity: {answers.get('digitalMaturity', 'unknown')}/4",
        f"Customer Feedback: {answers.get('customerFeedback', 'unknown')}",
        f"",
        f"Strategic Goals: {answers.get('strategicGoals', '')}",
        f"Strategic Priority: {answers.get('strategicPriority', 'unknown')}",
        f"Time Horizon: {answers.get('timeHorizon', 'unknown')}",
        f"Risk Appetite: {answers.get('riskAppetite', 'unknown')}",
        f"",
        f"Team Size: {answers.get('teamSize', 'unknown')}",
        f"Revenue Range: {answers.get('revenueRange', 'unknown')}",
        f"Estimated Innovation Budget: {budget}",
        f"Decision Making: {answers.get('decisionMaking', 'unknown')}",
        f"",
        f"Main Barriers: {', '.join(answers.get('mainBarrier', [])) or 'none'}",
        f"Competitive Pressure: {answers.get('competitivePressure', 'unknown')}",
        f"Regulatory Environment: {answers.get('regulatoryEnvironment', 'unknown')}",
        f"",
        f"Past Initiatives: {answers.get('pastInitiatives', 'None')}",
        f"Additional Context: {answers.get('additionalContext', 'None')}",
    ]

    if "previous_assessment" in inp:
        lines.append("")
        lines.append("--- PRIOR ASSESSMENT ---")
        prev = inp["previous_assessment"]
        pf = prev.get("fields", prev)
        lines.append(f"Company: {pf.get('companyName', '?')}")
        lines.append(f"Sector: {pf.get('sector', '?')}")
        lines.append(f"Risk: {pf.get('riskAppetite', '?')} | Priority: {pf.get('strategicPriority', '?')}")
        lines.append(f"Regulatory: {pf.get('regulatoryEnvironment', '?')} | Competition: {pf.get('competitivePressure', '?')}")
        lines.append(f"Budget: {pf.get('budgetPercentage', '?')}% of {pf.get('revenueRange', '?')}")
        if pf.get('mainBarrier'):
            lines.append(f"Barriers: {', '.join(pf.get('mainBarrier', []))}")
        lines.append("")
        lines.append(f"Changes since last assessment: {inp.get('changes_since_last', 'N/A')}")
        lines.append(f"Recommendation status: {json.dumps(inp.get('recommendation_status', {}))}")

    return "\n".join(lines)


def format_assistant_output(ex: dict) -> str:
    out = ex["output"]
    return json.dumps(out, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────────────────────────────────
# Convert to JSONL
# ──────────────────────────────────────────────────────────────────────

def convert(examples: list[dict]) -> list[dict]:
    records = []
    first_instruction = (
        "You are a strategic corporate innovation advisor. "
        "Analyse the company profile and survey responses, then respond ONLY with "
        "a valid JSON object containing maturity_score, opportunities, next_steps, "
        "and key_weaknesses. Apply all constraints consistently: budget limits, "
        "regulatory burden, risk appetite alignment, competitive urgency, and "
        "strategic priority focus."
    )
    reassess_instruction = (
        "You are a strategic corporate innovation advisor conducting a reassessment. "
        "Analyse the prior assessment summary, changes since last assessment, "
        "and updated survey, then respond ONLY with a valid JSON object containing "
        "maturity_score, score_delta, score_change, opportunities with carry_forward "
        "tracking, next_steps, key_weaknesses, progress, and comparison_to_previous. "
        "Apply all constraints consistently."
    )
    for ex in examples:
        is_reassess = ex.get("assessment_type") == "reassessment"
        instruction = reassess_instruction if is_reassess else ex.get(
            "instruction", first_instruction
        )
        record = {
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": format_user_input(ex)},
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
