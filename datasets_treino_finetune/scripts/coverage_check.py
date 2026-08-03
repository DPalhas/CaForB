#!/usr/bin/env python3
"""
coverage_check.py — Validates distribution balance of generated survey inputs.

Reads raw_inputs.json and reports coverage across all structured dimensions,
flags gaps in the constraint combo grid, and ensures no bucket is starved.

Usage: python scripts/coverage_check.py [input_file]
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "raw_inputs.json"

SECTORS = [
    "Agriculture, Forestry & Fishing", "Mining & Extraction", "Manufacturing",
    "Construction", "Energy & Utilities", "Retail & Wholesale Trade",
    "E-commerce", "Transportation & Logistics", "Hospitality & Tourism",
    "Information Technology", "SaaS / Software", "Telecommunications",
    "Fintech", "Financial Services", "Insurance", "Real Estate",
    "Professional & Consulting Services", "Legal Services", "Education",
    "Healthtech", "Healthcare & Medical", "Pharmaceuticals & Biotech",
    "Arts, Entertainment & Media", "Public Administration", "Nonprofit / NGO", "Other",
]

SIZES = ["Micro", "Small", "Medium", "Large"]
RISK_APPETITES = ["conservative", "balanced", "bold"]
STRATEGIC_PRIORITIES = ["growth", "efficiency", "market_defense", "diversification"]
REGULATORY_ENVS = ["low", "medium", "high"]
COMPETITIVE_PRESSURES = ["low", "medium", "high"]

DIMENSIONS = [
    ("sector", SECTORS),
    ("size", SIZES),
    ("riskAppetite", RISK_APPETITES),
    ("strategicPriority", STRATEGIC_PRIORITIES),
    ("regulatoryEnvironment", REGULATORY_ENVS),
    ("competitivePressure", COMPETITIVE_PRESSURES),
]


def load_examples(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_distribution(examples: list[dict]):
    print("=" * 70)
    print("  DISTRIBUTION REPORT")
    print("=" * 70)
    print(f"  Total examples: {len(examples)}\n")

    all_ok = True

    for field_name, pool in DIMENSIONS:
        counts = defaultdict(int)
        for ex in examples:
            counts[ex["fields"][field_name]] += 1

        n = len(examples)
        expected = n / len(pool)
        min_c = min(counts[v] for v in pool)
        max_c = max(counts[v] for v in pool)
        deviation = max(abs(max_c - expected), abs(expected - min_c))
        pct_dev = (deviation / expected) * 100 if expected else 0

        status = "OK" if pct_dev <= 10 else "WARN"
        if status == "WARN":
            all_ok = False

        print(f"  [{status}] {field_name}:")
        print(f"         Expected: {expected:.1f}  Min: {min_c}  Max: {max_c}  "
              f"Deviation: {pct_dev:.1f}%")
        for val in pool:
            bar_w = int((counts[val] / expected) * 40) if expected else 0
            bar = "#" * bar_w
            delta = counts[val] - expected
            flag = ""
            if delta < -expected * 0.15:
                flag = " <-- LOW"
            elif delta > expected * 0.15:
                flag = " <-- HIGH"
            print(f"         {val:<22} {counts[val]:>3}  {bar}{flag}")
        print()

    return all_ok


def check_combos(examples: list[dict]):
    print("  CONSTRAINT COMBO GRID (riskAppetite | strategicPriority | regulatoryEnvironment)")
    print("  Target: >= 3 per combo\n")

    combo_counts = defaultdict(int)
    for ex in examples:
        combo_counts[ex["combo_id"]] += 1

    gaps = []
    for risk in RISK_APPETITES:
        for prio in STRATEGIC_PRIORITIES:
            for reg in REGULATORY_ENVS:
                combo_id = f"{risk}|{prio}|{reg}"
                count = combo_counts[combo_id]
                status = "OK" if count >= 3 else "GAP"
                symbol = "  " if count >= 3 else "!!"
                print(f"  [{status}] {symbol} {combo_id:<45} = {count}")
                if count < 3:
                    gaps.append(combo_id)

    return gaps


def check_correlations(examples: list[dict]):
    print("\n" + "=" * 70)
    print("  CORRELATION RULE CHECKS")
    print("=" * 70)

    issues = []

    for ex in examples:
        f = ex["fields"]

        if f["riskAppetite"] == "conservative" and f["budgetPercentage"] > 10:
            issues.append(f"{ex['id']}: conservative risk but budget={f['budgetPercentage']}% (unusually high)")

        if f["riskAppetite"] == "bold" and f["budgetPercentage"] < 5:
            issues.append(f"{ex['id']}: bold risk but budget={f['budgetPercentage']}% (unusually low)")

        if f["size"] == "Micro" and f["revenueRange"] == "over_50m":
            issues.append(f"{ex['id']}: Micro size with over_50m revenue (unlikely)")

        if f["size"] == "Large" and f["revenueRange"] == "under_1m":
            issues.append(f"{ex['id']}: Large size with under_1m revenue (unlikely)")

        if f["innovationProcess"] == "none" and f["customerFeedback"] == "dedicated_research":
            issues.append(f"{ex['id']}: no innovation process but dedicated feedback research (contradiction)")

        if f["innovationProcess"] == "formal" and f["digitalMaturity"] == "1":
            issues.append(f"{ex['id']}: formal innovation process but digital maturity=1 (contradiction)")

    if issues:
        print(f"\n  Found {len(issues)} correlation warnings (first 10):")
        for issue in issues[:10]:
            print(f"    - {issue}")
    else:
        print("\n  No correlation rule violations found.")
    print()


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT

    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        sys.exit(1)

    examples = load_examples(input_path)

    dist_ok = check_distribution(examples)
    gaps = check_combos(examples)
    check_correlations(examples)

    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Distribution: {'PASS' if dist_ok else 'WARNINGS FOUND'}")
    print(f"  Constraint gaps: {len(gaps)} of 36")
    if gaps:
        for g in gaps:
            print(f"    - {g}")
    print()

    return 0 if dist_ok and not gaps else 1


if __name__ == "__main__":
    sys.exit(main())
