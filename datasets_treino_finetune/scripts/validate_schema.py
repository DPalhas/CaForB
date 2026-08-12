#!/usr/bin/env python3
"""
validate_schema.py — Phase 3: Schema and quality validation of generated training examples.

Checks all 504 examples for:
  1. Schema completeness (all required keys, non-empty arrays)
  2. Score range validity (float 0-10)
  3. Risk appetite vs opportunity type consistency
  4. Budget sanity (resource asks vs estimated budget)
  5. Regulatory alignment (high regulation → compliance steps)
  6. Strategic priority alignment (opportunities serve stated priority)
  7. Near-duplicate detection (weaknesses cloned across same sector)

Usage:
    python scripts/validate_schema.py
    python scripts/validate_schema.py --verbose
    python scripts/validate_schema.py --report final/validation_report.json
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw"
REPORT_PATH = BASE_DIR / "final" / "validation_report.json"

ALL_BARRIERS = ["budget", "talent", "process", "culture", "time", "strategy"]
RISK_APPETITES = ["conservative", "balanced", "bold"]
STRATEGIC_PRIORITIES = ["growth", "efficiency", "market_defense", "diversification"]
REGULATORY_ENVS = ["low", "medium", "high"]
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

REVENUE_RANGE_MIDPOINTS = {
    "under_1m": 500_000,
    "1m_to_10m": 5_500_000,
    "10m_to_50m": 30_000_000,
    "over_50m": 75_000_000,
}

COMPLIANCE_KEYWORDS = [
    "compliance", "legal review", "regulatory", "certification",
    "iso ", "gdpr", "hipaa", "audit", "standards body", "regulator",
    "data protection", "psd2", "sox", "soc 2", "fda", "ema"
]

EFFICIENCY_KEYWORDS = [
    "cost", "efficiency", "automation", "optimize", "reduce", "saving",
    "productivity", "throughput", "streamline", "cut", "eliminate waste",
    "faster", "cheaper", "lean", "operational", "process improvement",
    "reduction", "cycle time", "bottleneck", "opex", "unit cost"
]

GROWTH_KEYWORDS = [
    "revenue", "growth", "market share", "expansion", "new market",
    "customer acquisition", "sales", "upsell", "cross-sell", "enter",
    "launch", "scale", "penetration", "customer base", "monetize",
    "pricing", "subscription", "recurring revenue", "churn reduction",
]

DEFENSE_KEYWORDS = [
    "retention", "defend", "competitive moat", "switching cost",
    "loyalty", "churn", "counter", "differentiate", "stickiness",
    "protect", "market position", "incumbent", "competitor",
]

DIVERSIFICATION_KEYWORDS = [
    "diversify", "new vertical", "new business model", "adjacent",
    "new product line", "new segment", "new industry", "pivot",
    "alternative revenue", "new channel", "partnership", "acquisition",
]

PRIORITY_KEYWORDS = {
    "growth": GROWTH_KEYWORDS,
    "efficiency": EFFICIENCY_KEYWORDS,
    "market_defense": DEFENSE_KEYWORDS,
    "diversification": DIVERSIFICATION_KEYWORDS,
}


# ──────────────────────────────────────────────────────────────────────

def load_examples() -> list[dict]:
    files = sorted(RAW_DIR.glob("*.json"))
    examples = []
    for fp in files:
        try:
            d = json.loads(fp.read_text(encoding="utf-8"))
            d["_file"] = fp.name
            examples.append(d)
        except (json.JSONDecodeError, KeyError) as e:
            examples.append({"_file": fp.name, "_error": str(e)})
    return examples


# ──────────────────────────────────────────────────────────────────────
# 1. Schema completeness
# ──────────────────────────────────────────────────────────────────────

def check_schema(ex: dict) -> list[str]:
    issues = []
    if "_error" in ex:
        issues.append(f"FILE CORRUPTED: {ex['_error']}")
        return issues

    top_keys = ["id", "input", "output"]
    for k in top_keys:
        if k not in ex:
            issues.append(f"SCHEMA: missing top-level key '{k}'")

    inp = ex.get("input", {})
    if "company" not in inp:
        issues.append("SCHEMA: missing input.company")
    if "answers" not in inp:
        issues.append("SCHEMA: missing input.answers")
    else:
        required_answers = [
            "regulatoryEnvironment", "innovationProcess", "customerFeedback",
            "strategicPriority", "strategicGoals", "timeHorizon", "riskAppetite",
            "teamSize", "digitalMaturity", "revenueRange", "budgetPercentage",
            "decisionMaking", "mainBarrier", "competitivePressure",
            "companyDescription", "pastInitiatives", "additionalContext",
        ]
        for ra in required_answers:
            if ra not in inp["answers"]:
                issues.append(f"SCHEMA: missing input.answers.{ra}")

    out = ex.get("output", {})
    if "maturity_score" not in out:
        issues.append("SCHEMA: missing output.maturity_score")
    if "opportunities" not in out:
        issues.append("SCHEMA: missing output.opportunities")
    elif not isinstance(out["opportunities"], list):
        issues.append("SCHEMA: output.opportunities is not an array")
    elif len(out["opportunities"]) == 0:
        issues.append("SCHEMA: output.opportunities is empty")

    if "next_steps" not in out:
        issues.append("SCHEMA: missing output.next_steps")
    elif not isinstance(out["next_steps"], list):
        issues.append("SCHEMA: output.next_steps is not an array")

    if "key_weaknesses" not in out:
        issues.append("SCHEMA: missing output.key_weaknesses")
    elif not isinstance(out["key_weaknesses"], list):
        issues.append("SCHEMA: output.key_weaknesses is not an array")

    return issues


# ──────────────────────────────────────────────────────────────────────
# 2. Score range
# ──────────────────────────────────────────────────────────────────────

def check_score(ex: dict) -> list[str]:
    issues = []
    score = ex.get("output", {}).get("maturity_score")
    if score is not None:
        if not isinstance(score, (int, float)):
            issues.append(f"SCORE: maturity_score={score} is not numeric")
        elif score < 0 or score > 10:
            issues.append(f"SCORE: maturity_score={score} out of 0-10 range")
    return issues


# ──────────────────────────────────────────────────────────────────────
# 3. Risk appetite vs opportunity types
# ──────────────────────────────────────────────────────────────────────

def check_risk_alignment(ex: dict) -> list[str]:
    issues = []
    ra = ex.get("input", {}).get("answers", {}).get("riskAppetite", "")
    opps = ex.get("output", {}).get("opportunities", [])

    if not opps or ra not in RISK_APPETITES:
        return issues

    types = [o.get("type", "").lower() for o in opps if isinstance(o, dict)]
    radical_count = sum(1 for t in types if t == "radical")
    incremental_count = sum(1 for t in types if t == "incremental")

    if ra == "conservative" and radical_count > 0:
        issues.append(
            f"RISK: conservative risk appetite has {radical_count} radical opportunity(s) "
            f"(expect all incremental, got {types})"
        )

    if ra == "bold" and radical_count == 0:
        issues.append(
            f"RISK: bold risk appetite has 0 radical opportunities (expect >= 1, got {types})"
        )

    return issues


# ──────────────────────────────────────────────────────────────────────
# 4. Budget sanity
# ──────────────────────────────────────────────────────────────────────

def estimate_budget_eu(ex: dict) -> int | None:
    answers = ex.get("input", {}).get("answers", {})
    pct = answers.get("budgetPercentage")
    revenue_key = answers.get("revenueRange")
    if pct is None or not revenue_key:
        return None
    midpoint = REVENUE_RANGE_MIDPOINTS.get(revenue_key)
    if midpoint is None:
        return None
    return int(midpoint * (pct / 100))


def check_budget_sanity(ex: dict) -> list[str]:
    issues = []
    budget = estimate_budget_eu(ex)
    if budget is None:
        return issues

    opps = ex.get("output", {}).get("opportunities", [])

    expensive_patterns = [
        (r"\bhire\b.*\b(\d+)\b.*\b(engineer|developer|scientist|specialist|consultant)\b", "hire specialist"),
        (r"\b(€|EUR|EUR\s*)?(\d{2,3}[.,]\d{3})\b", "specific large cost"),
        (r"\b(\d+)\s*(million|M)\b", "million-range spend"),
        (r"\benterprise\b.*\blicense\b", "enterprise license"),
        (r"\bpurchase\b.*\bserver\b", "hardware purchase"),
    ]

    for o in opps:
        if not isinstance(o, dict):
            continue
        plan = o.get("execution_plan", {})
        resources = plan.get("resources_needed", [])
        resource_text = " ".join(str(r) for r in resources)

        for pattern, label in expensive_patterns:
            if re.search(pattern, resource_text, re.IGNORECASE):
                if budget < 100_000 and label in ("hire specialist", "enterprise license", "hardware purchase"):
                    issues.append(
                        f"BUDGET: estimated budget=~EUR{budget:,} but resource asks for '{label}' "
                        f"in opportunity '{o.get('title','')[:50]}'"
                    )
                if budget < 500_000 and label == "million-range spend":
                    issues.append(
                        f"BUDGET: estimated budget=~EUR{budget:,} but resource mentions millions "
                        f"in opportunity '{o.get('title','')[:50]}'"
                    )
                break

    return issues


# ──────────────────────────────────────────────────────────────────────
# 5. Regulatory alignment
# ──────────────────────────────────────────────────────────────────────

def check_regulatory(ex: dict) -> list[str]:
    issues = []
    reg = ex.get("input", {}).get("answers", {}).get("regulatoryEnvironment", "")
    if reg != "high":
        return issues

    opps = ex.get("output", {}).get("opportunities", [])
    for i, o in enumerate(opps):
        if not isinstance(o, dict):
            continue
        plan = o.get("execution_plan", {})
        actions = plan.get("first_actions", [])
        action_text = " ".join(str(a) for a in actions).lower()

        has_compliance = any(kw in action_text for kw in COMPLIANCE_KEYWORDS)
        if not has_compliance:
            issues.append(
                f"REG: high regulatory env but opportunity {i+1} "
                f"'{o.get('title','')[:50]}' has no compliance/legal step in first_actions"
            )

    return issues


# ──────────────────────────────────────────────────────────────────────
# 6. Strategic priority alignment
# ──────────────────────────────────────────────────────────────────────

def check_priority_alignment(ex: dict) -> list[str]:
    issues = []
    sp = ex.get("input", {}).get("answers", {}).get("strategicPriority", "")
    keywords = PRIORITY_KEYWORDS.get(sp, [])
    if not keywords:
        return issues

    opps = ex.get("output", {}).get("opportunities", [])
    if len(opps) < 2:
        return issues

    aligned = 0
    for o in opps:
        if not isinstance(o, dict):
            continue
        text = (o.get("title", "") + " " + o.get("rationale", "")).lower()
        if any(kw in text for kw in keywords):
            aligned += 1

    threshold = max(1, len(opps) * 0.4)
    if aligned < threshold:
        issues.append(
            f"PRIORITY: strategicPriority={sp} but only {aligned}/{len(opps)} "
            f"opportunities use {sp}-related language (threshold={threshold:.0f})"
        )

    return issues


# ──────────────────────────────────────────────────────────────────────
# 7. Duplicate detection (weaknesses per sector)
# ──────────────────────────────────────────────────────────────────────

def check_duplicates(examples: list[dict]) -> list[dict]:
    from difflib import SequenceMatcher

    sector_weaknesses: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for ex in examples:
        if "_error" in ex:
            continue
        sector = ex.get("input", {}).get("company", {}).get("sector", "unknown")
        weaks = ex.get("output", {}).get("key_weaknesses", [])
        for w in weaks:
            sector_weaknesses[sector].append((ex["_file"], str(w).lower().strip()))

    issues_per_file: dict[str, list[str]] = defaultdict(list)

    for sector, entries in sector_weaknesses.items():
        for i, (file_a, w_a) in enumerate(entries):
            for j, (file_b, w_b) in enumerate(entries):
                if j <= i:
                    continue
                ratio = SequenceMatcher(None, w_a, w_b).ratio()
                if ratio > 0.85:
                    issues_per_file[file_a].append(
                        f"DUPLICATE: weakness '{w_a[:60]}' is {ratio:.0%} similar to "
                        f"'{w_b[:60]}' in {file_b} (both sector={sector})"
                    )
                    issues_per_file[file_b].append(
                        f"DUPLICATE: weakness '{w_b[:60]}' is {ratio:.0%} similar to "
                        f"'{w_a[:60]}' in {file_a} (both sector={sector})"
                    )

    return [
        {"file": f, "issues": v, "severity": "warning"}
        for f, v in issues_per_file.items()
    ]


# ──────────────────────────────────────────────────────────────────────
# Reassessment-specific checks
# ──────────────────────────────────────────────────────────────────────

VALID_CARRY_STATUSES = {"continues", "evolved_to", "retired", "new"}
VALID_SCORE_CHANGES = {"improved", "stable", "declined"}


def is_reassessment(ex: dict) -> bool:
    return ex.get("assessment_type") == "reassessment"


def check_reassessment_fields(ex: dict) -> list[str]:
    if not is_reassessment(ex):
        return []
    output = ex.get("output", {})
    issues = []
    if "score_delta" not in output:
        issues.append("missing score_delta (reassessment)")
    if "score_change" not in output:
        issues.append("missing score_change (reassessment)")
    elif output.get("score_change") not in VALID_SCORE_CHANGES:
        issues.append(f"invalid score_change: {output['score_change']}")
    if "progress" not in output:
        issues.append("missing progress block (reassessment)")
    if "comparison_to_previous" not in output:
        issues.append("missing comparison_to_previous (reassessment)")
    return issues


def check_carry_forward(ex: dict) -> list[str]:
    if not is_reassessment(ex):
        return []
    issues = []
    for i, opp in enumerate(ex.get("output", {}).get("opportunities", [])):
        cfs = opp.get("carry_forward_status")
        if cfs and cfs not in VALID_CARRY_STATUSES:
            issues.append(f"opportunity {i}: invalid carry_forward_status '{cfs}'")
        cff = opp.get("carry_forward_from")
        if cfs == "new" and cff:
            issues.append(f"opportunity {i}: new with carry_forward_from='{cff}'")
        if cfs and cfs != "new" and not cff:
            issues.append(f"opportunity {i}: {cfs} but no carry_forward_from")
    return issues


def check_score_delta_consistency(ex: dict) -> list[str]:
    if not is_reassessment(ex):
        return []
    output = ex.get("output", {})
    ms = output.get("maturity_score")
    sd = output.get("score_delta")
    cp = output.get("comparison_to_previous", {})
    ps = cp.get("previous_score")
    if ms is not None and sd is not None and ps is not None:
        delta = ms - ps
        if abs(sd - delta) > 1.0:
            return [f"score_delta {sd} inconsistent with {ms} - {ps} = {delta:.1f}"]
    return []


def check_progress_structure(ex: dict) -> list[str]:
    if not is_reassessment(ex):
        return []
    progress = ex.get("output", {}).get("progress", {})
    issues = []
    for field in ("improvements", "persistent_gaps", "achieved_milestones"):
        if field not in progress:
            issues.append(f"progress missing '{field}'")
    return issues


def check_comparison_structure(ex: dict) -> list[str]:
    if not is_reassessment(ex):
        return []
    cp = ex.get("output", {}).get("comparison_to_previous", {})
    issues = []
    for field in ("previous_score", "previous_date", "assessment_number", "key_changes"):
        if field not in cp:
            issues.append(f"comparison_to_previous missing '{field}'")
    return issues


# ──────────────────────────────────────────────────────────────────────
# Run all checks
# ──────────────────────────────────────────────────────────────────────

def run_validation(verbose: bool = False) -> dict:
    examples = load_examples()
    total = len(examples)
    print(f"Validating {total} examples...\n")

    results = {
        "total": total,
        "pass": 0,
        "fail": 0,
        "errors": [],
        "warnings": [],
        "summary": {},
    }

    checks = [
        ("schema", check_schema, "error"),
        ("score", check_score, "error"),
        ("risk_alignment", check_risk_alignment, "error"),
        ("budget_sanity", check_budget_sanity, "warning"),
        ("regulatory", check_regulatory, "warning"),
        ("priority_alignment", check_priority_alignment, "warning"),
        ("reassessment_fields", check_reassessment_fields, "error"),
        ("carry_forward", check_carry_forward, "error"),
        ("score_delta_consistency", check_score_delta_consistency, "warning"),
        ("progress_structure", check_progress_structure, "warning"),
        ("comparison_structure", check_comparison_structure, "warning"),
    ]

    issue_counts = Counter()
    per_file_issues: dict[str, list[dict]] = defaultdict(list)

    for ex in examples:
        file_name = ex.get("_file", "unknown")
        file_has_error = False

        for check_name, check_fn, severity in checks:
            issues = check_fn(ex)
            for issue in issues:
                issue_counts[check_name] += 1
                entry = {"file": file_name, "issue": issue, "severity": severity}
                per_file_issues[file_name].append(entry)
                results[severity + "s"].append(entry)
                if severity == "error":
                    file_has_error = True
                if verbose:
                    tag = "ERROR" if severity == "error" else "WARN"
                    print(f"  [{tag}] {file_name}: {issue}")

        if file_has_error:
            results["fail"] += 1
        else:
            results["pass"] += 1

    # Cross-file duplicate check
    dup_entries = check_duplicates(examples)
    for dup in dup_entries:
        for issue in dup["issues"]:
            entry = {"file": dup["file"], "issue": issue, "severity": "warning"}
            per_file_issues[dup["file"]].append(entry)
            results["warnings"].append(entry)
            issue_counts["duplicates"] += 1

    results["summary"] = dict(issue_counts)
    results["by_file"] = {
        f: [i["issue"] for i in issues]
        for f, issues in sorted(per_file_issues.items())
    }

    return results


# ──────────────────────────────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────────────────────────────

def print_report(results: dict):
    print(f"\n{'='*60}")
    print(f"  VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"  Total:  {results['total']}")
    print(f"  Pass:   {results['pass']}")
    print(f"  Fail:   {results['fail']}")
    print(f"  Errors: {len(results['errors'])}")
    print(f"  Warnings: {len(results['warnings'])}")
    print()

    print(f"  Issues by category:")
    for check_name, count in sorted(results["summary"].items()):
        bar = "#" * min(count, 50)
        print(f"    {check_name:<25} {count:>3}  {bar}")

    if results["errors"]:
        print(f"\n  --- ERRORS (blocking) ---")
        for e in results["errors"][:20]:
            print(f"    {e['file']}: {e['issue']}")
        if len(results["errors"]) > 20:
            print(f"    ... and {len(results['errors'])-20} more")

    if results["warnings"]:
        print(f"\n  --- WARNINGS (review) ---")
        shown = 0
        for w in results["warnings"]:
            if "DUPLICATE" in w["issue"]:
                continue  # duplicates are verbose
            if shown < 10:
                print(f"    {w['file']}: {w['issue']}")
            shown += 1
        if shown > 10:
            print(f"    ... and {shown - 10} more")

    dup_count = sum(1 for w in results["warnings"] if "DUPLICATE" in w["issue"])
    if dup_count:
        print(f"\n  --- DUPLICATE WEAKNESSES: {dup_count} near-duplicates found ---")


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate generated training examples.")
    parser.add_argument("--verbose", action="store_true", help="Print every issue")
    parser.add_argument("--report", type=str, default=None, help="Save JSON report to path")
    args = parser.parse_args()

    if not RAW_DIR.exists() or not list(RAW_DIR.glob("*.json")):
        print("Error: no files found in raw/ directory")
        sys.exit(1)

    results = run_validation(verbose=args.verbose)
    print_report(results)

    report_path = Path(args.report) if args.report else REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nReport saved to {report_path}")

    if results["fail"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
