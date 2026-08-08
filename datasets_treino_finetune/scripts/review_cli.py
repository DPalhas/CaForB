#!/usr/bin/env python3
"""
review_cli.py — Interactive expert review CLI for fine-tuning examples.

Loads generated training examples, displays survey input + LLM output side-by-side,
lets the expert correct scores, fix opportunity types, and mark files as reviewed.

Usage:
    python scripts/review_cli.py              # Review all unreviewed, starting with errors
    python scripts/review_cli.py --errors     # Review only examples with risk/regulatory issues
    python scripts/review_cli.py --id 0042    # Review a specific example
    python scripts/review_cli.py --sample 20  # Random sample of 20 unreviewed
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import random

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw"

RISK_APPETITES = ["conservative", "balanced", "bold"]
ALL_SECTORS = [
    "Agriculture, Forestry & Fishing", "Mining & Extraction", "Manufacturing",
    "Construction", "Energy & Utilities", "Retail & Wholesale Trade",
    "E-commerce", "Transportation & Logistics", "Hospitality & Tourism",
    "Information Technology", "SaaS / Software", "Telecommunications",
    "Fintech", "Financial Services", "Insurance", "Real Estate",
    "Professional & Consulting Services", "Legal Services", "Education",
    "Healthtech", "Healthcare & Medical", "Pharmaceuticals & Biotech",
    "Arts, Entertainment & Media", "Public Administration", "Nonprofit / NGO", "Other",
]

COMPLIANCE_KEYWORDS = [
    "compliance", "legal", "regulatory", "certification", "iso",
    "gdpr", "hipaa", "audit", "standards", "regulator", "data protection",
]


# ──────────────────────────────────────────────────────────────────────
# Classification — which files need review most
# ──────────────────────────────────────────────────────────────────────

def classify(ex: dict) -> dict:
    """Return {status, issues} for an example."""
    issues = []
    ra = ex.get("input", {}).get("answers", {}).get("riskAppetite", "")
    reg = ex.get("input", {}).get("answers", {}).get("regulatoryEnvironment", "")
    opps = ex.get("output", {}).get("opportunities", [])

    types = [o.get("type", "").lower() for o in opps if isinstance(o, dict)]
    radical_count = sum(1 for t in types if t == "radical")

    if ra == "conservative" and radical_count > 0:
        issues.append("conservative_risk_with_radical_opps")

    if reg == "high":
        has_compliance = False
        for o in opps:
            if not isinstance(o, dict):
                continue
            actions = o.get("execution_plan", {}).get("first_actions", [])
            text = " ".join(str(a) for a in actions).lower()
            if any(kw in text for kw in COMPLIANCE_KEYWORDS):
                has_compliance = True
                break
        if not has_compliance:
            issues.append("high_reg_without_compliance")

    metadata = ex.get("metadata", {})
    reviewed = metadata.get("reviewed", False)

    if issues:
        return {"status": "error", "issues": issues, "reviewed": reviewed}
    if reviewed:
        return {"status": "reviewed", "issues": [], "reviewed": True}
    return {"status": "clean", "issues": [], "reviewed": False}


def get_issue_counts(examples: list[dict]) -> dict:
    counts = {"error": 0, "clean": 0, "reviewed": 0, "total": len(examples)}
    for ex in examples:
        c = classify(ex)
        counts[c["status"]] += 1
    return counts


# ──────────────────────────────────────────────────────────────────────
# Display helpers
# ──────────────────────────────────────────────────────────────────────

SEP = "-" * 60
THIN = "." * 60


def _print_box(title: str, content: str, color: str = ""):
    print(f"\n  {SEP}")
    print(f"  {title}")
    print(f"  {SEP}")
    for line in content.strip().split("\n"):
        print(f"  {line}")


def display_example(ex: dict, idx: int, total: int):
    """Show the full example for review."""
    company = ex["input"]["company"]
    answers = ex["input"]["answers"]
    output = ex["output"]
    metadata = ex.get("metadata", {})

    classification = classify(ex)
    status_tag = classification["status"]
    issues_tag = ", ".join(classification["issues"]) if classification["issues"] else "none"
    reviewed_tag = "Yes" if classification["reviewed"] else "No"

    print(f"\n{'='*60}")
    print(f"  [{idx+1}/{total}]  {ex['id']}.json")
    print(f"  Status: {status_tag.upper()}  |  Issues: {issues_tag}  |  Reviewed: {reviewed_tag}")
    if metadata.get("reviewer_notes"):
        print(f"  Notes: {metadata['reviewer_notes']}")

    print(f"\n  {'-'*20} SURVEY INPUT {'-'*20}")
    print(f"  Company:    {company.get('name', '?')}")
    print(f"  Sector:     {company.get('sector', '?')}")
    print(f"  Size:       {company.get('size', '?')}")
    print(f"  Revenue:    {answers.get('revenueRange', '?')}")
    print(f"  Budget:     {answers.get('budgetPercentage', '?')}%")
    print(f"")
    print(f"  Risk:       {answers.get('riskAppetite', '?')}")
    print(f"  Priority:   {answers.get('strategicPriority', '?')}")
    print(f"  Regulation: {answers.get('regulatoryEnvironment', '?')}")
    print(f"  Competition:{answers.get('competitivePressure', '?')}")
    print(f"  Time:       {answers.get('timeHorizon', '?')}")
    print(f"")
    print(f"  Process:    {answers.get('innovationProcess', '?')}")
    print(f"  Digital:    {answers.get('digitalMaturity', '?')}/4")
    print(f"  Feedback:   {answers.get('customerFeedback', '?')}")
    print(f"  Decision:   {answers.get('decisionMaking', '?')}")
    print(f"  Barriers:   {', '.join(answers.get('mainBarrier', [])) or 'none'}")
    print(f"")
    print(f"  Description: {answers.get('companyDescription', '')[:200]}...")
    print(f"  Goals:       {answers.get('strategicGoals', '')[:200]}...")

    print(f"\n  {'-'*20} LLM OUTPUT {'-'*20}")
    score = output.get("maturity_score", "?")
    print(f"  Maturity Score: {score} / 10")
    print(f"")

    opps = output.get("opportunities", [])
    for i, o in enumerate(opps):
        if not isinstance(o, dict):
            continue
        plan = o.get("execution_plan", {})
        actions = plan.get("first_actions", [])
        print(f"  [{o.get('type', '?').upper():>11}] {o.get('title', '?')}")
        print(f"         Impact: {o.get('impact', '?')}  Difficulty: {o.get('difficulty', '?')}  Timeframe: {o.get('timeframe', '?')}")
        print(f"         Rationale: {o.get('rationale', '')[:120]}...")
        if actions:
            print(f"         First actions: {actions[0][:100]}...")
        print()

    steps = output.get("next_steps", [])
    print(f"  Next Steps ({len(steps)}):")
    for s in steps:
        if isinstance(s, dict):
            print(f"    - {s.get('action', '?')}  [{s.get('owner', '?')} | {s.get('timeframe', '?')}]")

    weaknesses = output.get("key_weaknesses", [])
    print(f"\n  Key Weaknesses ({len(weaknesses)}):")
    for w in weaknesses:
        print(f"    - {w}")

    print(f"\n  {THIN}")


# ──────────────────────────────────────────────────────────────────────
# Edit actions
# ──────────────────────────────────────────────────────────────────────

def edit_score(ex: dict):
    output = ex["output"]
    current = output.get("maturity_score", 0)
    print(f"\n  Current score: {current}")
    raw = input("  New score (0-10, Enter to keep): ").strip()
    if raw:
        try:
            new_score = float(raw)
            if 0 <= new_score <= 10:
                output["maturity_score"] = new_score
                print(f"  Updated: {current} -> {new_score}")
            else:
                print("  Must be 0-10, unchanged.")
        except ValueError:
            print("  Invalid number, unchanged.")


def edit_opportunity_types(ex: dict):
    opps = ex["output"].get("opportunities", [])
    if not opps:
        print("  No opportunities to edit.")
        return

    print()
    for i, o in enumerate(opps):
        if not isinstance(o, dict):
            continue
        print(f"  [{i}] {o.get('type', '?'):>11} | {o.get('title', '?')[:70]}")

    choice = input("  Enter number to toggle, or Enter to skip: ").strip()
    if not choice:
        return
    try:
        idx = int(choice)
        opp = opps[idx]
        current = opp.get("type", "incremental")
        new_type = "radical" if current == "incremental" else "incremental"
        opp["type"] = new_type
        print(f"  [{idx}] {current} -> {new_type}")
    except (ValueError, IndexError):
        print("  Invalid selection.")


def add_compliance_step(ex: dict):
    opps = ex["output"].get("opportunities", [])
    reg = ex.get("input", {}).get("answers", {}).get("regulatoryEnvironment", "")

    print()
    for i, o in enumerate(opps):
        if not isinstance(o, dict):
            continue
        actions = o.get("execution_plan", {}).get("first_actions", [])
        print(f"  [{i}] {o.get('title', '?')[:70]}")
        print(f"       Actions: {actions}")

    choice = input("  Enter opportunity # to add compliance step, or Enter to skip: ").strip()
    if not choice:
        return
    try:
        idx = int(choice)
        opp = opps[idx]
        sector = ex.get("input", {}).get("company", {}).get("sector", "")
        domain_hint = "GDPR/data privacy" if "Tech" in sector or "SaaS" in sector or "Fintech" in sector else \
                      "regulatory standards" if reg == "high" else "industry best practices"
        step = f"Conduct {domain_hint} compliance review with legal team"
        opp["execution_plan"]["first_actions"].append(step)
        print(f"  Added: {step}")
    except (ValueError, IndexError, KeyError):
        print("  Invalid selection or malformed opportunity.")


# ──────────────────────────────────────────────────────────────────────
# Save & mark reviewed
# ──────────────────────────────────────────────────────────────────────

def save_example(ex: dict):
    fp = RAW_DIR / f"{ex['id']}.json"
    metadata = ex.setdefault("metadata", {})
    metadata["reviewed"] = True
    metadata["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    fp.write_text(json.dumps(ex, indent=2, ensure_ascii=False), encoding="utf-8")


def add_note(ex: dict):
    current = ex.get("metadata", {}).get("reviewer_notes", "")
    note = input("  Note (Enter to keep): ").strip()
    if note:
        ex.setdefault("metadata", {})["reviewer_notes"] = note


# ──────────────────────────────────────────────────────────────────────
# Interactive loop
# ──────────────────────────────────────────────────────────────────────

def interactive_review(indices: list[int], examples: list[dict]):
    total = len(indices)
    idx = 0
    reviewed_this_session = 0
    skipped_this_session = 0

    while 0 <= idx < len(indices):
        global_idx = indices[idx]
        ex = examples[global_idx]

        display_example(ex, idx, total)

        print("  [a]ccept  [s]core  [t]oggle type  [c]ompliance step  [n]ote  [q]uit  [j]ump  [k]skip")
        cmd = input("  > ").strip().lower()

        if cmd in ("a", ""):
            add_note(ex)
            save_example(ex)
            reviewed_this_session += 1
            print(f"  [OK] Accepted. ({reviewed_this_session} reviewed this session)")
            idx += 1

        elif cmd == "s":
            edit_score(ex)
            save_example(ex)

        elif cmd == "t":
            edit_opportunity_types(ex)
            save_example(ex)

        elif cmd == "c":
            add_compliance_step(ex)
            save_example(ex)

        elif cmd == "n":
            add_note(ex)
            save_example(ex)

        elif cmd == "k":
            skipped_this_session += 1
            print(f"  Skipped. ({skipped_this_session} skipped this session)")
            idx += 1

        elif cmd == "q":
            print(f"\n  Saved progress. {reviewed_this_session} reviewed, {skipped_this_session} skipped.")
            break

        elif cmd == "j":
            target = input("  Jump to example # (1-indexed, 0=end): ").strip()
            try:
                t = int(target)
                if t == 0:
                    idx = len(indices) - 1
                elif 1 <= t <= total:
                    idx = t - 1
                else:
                    print("  Out of range.")
            except ValueError:
                print("  Invalid number.")

        else:
            print("  Unknown command. Use: a s t c n q j k")

    print(f"\n  Session complete: {reviewed_this_session} reviewed, {skipped_this_session} skipped.")


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Interactive expert review of training examples.")
    parser.add_argument("--errors", action="store_true", help="Review only files with detected issues")
    parser.add_argument("--sample", type=int, default=0, help="Review a random sample of N unreviewed files")
    parser.add_argument("--id", type=str, default=None, help="Review a specific example ID (e.g. 0042)")
    parser.add_argument("--unreviewed", action="store_true", help="Review all unreviewed (default)")
    args = parser.parse_args()

    if not RAW_DIR.exists():
        print("Error: raw/ directory not found")
        sys.exit(1)

    # Load all examples
    examples = []
    for fp in sorted(RAW_DIR.glob("*.json")):
        ex = json.loads(fp.read_text(encoding="utf-8"))
        examples.append(ex)

    if not examples:
        print("No examples found.")
        sys.exit(1)

    # Classify
    classifications = [classify(ex) for ex in examples]

    # Build priority index lists
    error_indices = [i for i, c in enumerate(classifications) if c["status"] == "error" and not c["reviewed"]]
    clean_indices = [i for i, c in enumerate(classifications) if c["status"] == "clean" and not c["reviewed"]]
    all_unreviewed = error_indices + clean_indices

    reviewed_count = sum(1 for c in classifications if c["reviewed"])
    error_count = len(error_indices)
    clean_count = len(clean_indices)

    print(f"  Total: {len(examples)}  |  Reviewed: {reviewed_count}")
    print(f"  Errors (unreviewed): {error_count}  |  Clean (unreviewed): {clean_count}")
    print()

    # Select indices to review
    if args.id:
        target_id = args.id if args.id.endswith(".json") else f"{args.id}.json"
        review_indices = [i for i, ex in enumerate(examples) if target_id in ex.get("id", "")]
        if not review_indices:
            print(f"  Error: no example matching '{args.id}' found")
            sys.exit(1)
        print(f"  Reviewing specific file: {target_id}")

    elif args.errors:
        review_indices = error_indices
        print(f"  Reviewing {len(review_indices)} examples with detected issues")

    elif args.sample > 0:
        pool = all_unreviewed if all_unreviewed else list(range(len(examples)))
        k = min(args.sample, len(pool))
        review_indices = sorted(random.sample(pool, k))
        print(f"  Random sample of {k} unreviewed examples")

    else:
        review_indices = all_unreviewed
        print(f"  Reviewing {len(review_indices)} unreviewed examples (errors first)")

    if not review_indices:
        print("  Nothing to review. All files are either reviewed or clean.")
        return

    print(f"\n  Commands: (a)ccept  (s)core  (t)oggle type  (c)ompliance  (n)ote  (k)skip  (q)uit  (j)ump")
    print()

    interactive_review(review_indices, examples)


if __name__ == "__main__":
    main()
