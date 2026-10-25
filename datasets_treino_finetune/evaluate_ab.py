#!/usr/bin/env python3
"""
evaluate_ab.py — A/B evaluation of gemma4:12B vs caforb-v1 on held-out profiles.

Selects one profile per (risk x strategic priority x regulatory) cell from the
held-out validation split (the 184 records excluded from QLoRA training), runs
each profile through both models using the runtime self-correcting loop
(`generate_innovation_insight`), scores every output against the same business
rules that validated the training data (`validate_schema.py`), and reports
reliability, latency, rule-pass and completeness metrics plus paired statistics
(McNemar's test and Wilson intervals).

The run is grouped by model (all `gemma4:12B` generations first, then all
`caforb-v1`) so a single 8 GB GPU is not thrashed by reloading models between
every submission.

Requires Ollama to be running with both models available:
    ollama serve
    ollama pull gemma4:12B
    ollama create caforb-v1 -f Modelfile

Usage:
    python evaluate_ab.py --dry-run            # list the 36 selected profiles, no model calls
    python evaluate_ab.py --mock              # score the stored gold outputs (no Ollama)
    python evaluate_ab.py                     # full run (Ollama required)
    python evaluate_ab.py --reps 3 --subset-size 6
"""

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"
FINAL_DIR = BASE_DIR / "final"

# Make the CaForB app importable so the evaluation reuses the exact runtime
# generation loop and the exact training-data validation rules.
sys.path.insert(0, str(BASE_DIR.parent))          # CaForB root -> core.services
sys.path.insert(0, str(BASE_DIR / "scripts"))     # validate_schema

from core.services.llm_services import (          # noqa: E402
    generate_innovation_insight,
    _extract_json,
)
import validate_schema as vs                       # noqa: E402


MODELS = ["gemma4:12B", "caforb-v1"]
RISKS = ["conservative", "balanced", "bold"]
PRIORITIES = ["growth", "efficiency", "market_defense", "diversification"]
REGULATIONS = ["low", "medium", "high"]

# The (risk, priority, regulatory) cell that has no first-assessment record in
# the validation split, so a re-assessment profile is used for it instead.
REASSESSMENT_ONLY_CELL = ("bold", "diversification", "low")


# ──────────────────────────────────────────────────────────────────────
# Profile selection (held-out validation split)
# ──────────────────────────────────────────────────────────────────────

def _assistant_content(record: dict) -> str:
    for msg in record.get("messages", []):
        if msg.get("role") == "assistant":
            return msg["content"]
    return ""


def load_held_out_files() -> list[str]:
    """Return the raw/*.json filenames that belong to the validation split.

    The held-out split is identified by matching each raw file's serialised
    output against the assistant messages in final/validation.jsonl (the exact
    conversion produced by convert_to_jsonl.py). Everything else is train.
    """
    val_path = FINAL_DIR / "validation.jsonl"
    if not val_path.exists():
        raise FileNotFoundError(f"{val_path} not found")
    held_out = {
        _assistant_content(json.loads(line))
        for line in val_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    files = []
    for fp in sorted(RAW_DIR.glob("*.json")):
        d = json.loads(fp.read_text(encoding="utf-8"))
        if json.dumps(d.get("output", {}), ensure_ascii=False) in held_out:
            files.append(fp.name)
    return files


def _combo_of(raw: dict) -> tuple:
    a = raw.get("input", {}).get("answers", {})
    return (a.get("riskAppetite"), a.get("strategicPriority"),
            a.get("regulatoryEnvironment"))


def select_profiles() -> list[tuple]:
    """Return 36 (combo, filename, is_reassessment) profiles, one per cell.

    First assessments are preferred; a re-assessment is used only for the one
    cell that has no first-assessment record in the validation split.
    """
    files = load_held_out_files()
    by_cell = defaultdict(list)
    for fn in files:
        d = json.loads((RAW_DIR / fn).read_text(encoding="utf-8"))
        is_re = d.get("assessment_type") == "reassessment"
        by_cell[_combo_of(d)].append((fn, is_re))

    selected = []
    for cell in sorted(by_cell):
        firsts = [x for x in by_cell[cell] if not x[1]]
        reass = [x for x in by_cell[cell] if x[1]]
        pick = firsts[0] if firsts else reass[0]
        selected.append((cell, pick[0], pick[1]))
    return selected


# ──────────────────────────────────────────────────────────────────────
# History reconstruction for the single re-assessment profile
# ──────────────────────────────────────────────────────────────────────

def build_history(raw: dict) -> str:
    """Reconstruct the runtime `build_assessment_history` summary for a
    re-assessment profile from its base first-assessment output."""
    inp = raw.get("input", {})
    prev = inp.get("previous_assessment", {})
    base_id = prev.get("id")
    base = json.loads((RAW_DIR / f"{base_id}.json").read_text(encoding="utf-8"))
    out = base.get("output", {})

    rec_status = inp.get("recommendation_status", {}) or {}

    lines = ["---", "PRIOR ASSESSMENT SUMMARY", "---"]
    lines.append(f"Previous Maturity Score: {out.get('maturity_score')}")

    opps = out.get("opportunities", [])
    if opps:
        lines.append("\nPreviously Identified Opportunities:")
        for j, opp in enumerate(opps, 1):
            opp_id = opp.get("id", f"opp_{j}")
            status = rec_status.get(opp_id, "not tracked")
            lines.append(
                f'{j}. [{opp.get("type", "?")}] "{opp.get("title", "")}" '
                f'(Impact: {opp.get("impact", "?")}, '
                f'Difficulty: {opp.get("difficulty", "?")}, '
                f'Timeframe: {opp.get("timeframe", "?")})'
            )
            ep = opp.get("execution_plan") or {}
            if ep.get("success_metric"):
                lines.append(f'   KPI: {ep["success_metric"]}')
            lines.append(f"   Status: {status.upper()}")

    steps = out.get("next_steps", [])
    if steps:
        lines.append("\nPrevious Next Steps:")
        for k, step in enumerate(steps, 1):
            step_id = step.get("id", f"step_{k}")
            status = rec_status.get(step_id, "not tracked")
            lines.append(
                f'{k}. "{step.get("action", "")}" -> '
                f'Owner: {step.get("owner", "?")}, '
                f'Timeframe: {step.get("timeframe", "?")} -> {status.upper()}'
            )

    weaknesses = out.get("key_weaknesses", [])
    if weaknesses:
        lines.append("\nPrevious Key Weaknesses:")
        for w in weaknesses:
            lines.append(f"- {w}")

    lines += ["\n---", "BUDGET HISTORY:", "- Assessment #1: budget unknown", "---"]

    if inp.get("changes_since_last"):
        lines.append(f"\nCHANGES SINCE LAST ASSESSMENT:\n{inp['changes_since_last']}")

    if rec_status:
        lines.append("\nPROGRESS ON PREVIOUS RECOMMENDATIONS:")
        for key, value in rec_status.items():
            lines.append(f"- {key}: {value.upper()}")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# Generation + scoring
# ──────────────────────────────────────────────────────────────────────

def run_generation(company: dict, answers: dict, model: str,
                   history: str = None) -> dict:
    """Run one generation through the runtime loop; return parsed result."""
    steps = []

    def trace_cb(step_name, inp, out, duration_ms):
        steps.append((step_name, out, duration_ms))

    raw_text, total_ms = generate_innovation_insight(
        company, answers, history=history, model=model, trace_cb=trace_cb
    )
    parsed = _extract_json(raw_text) if raw_text else {}
    llm_calls = sum(1 for s in steps if s[0] == "llm_inference")
    retries = [s[0] for s in steps if s[0].startswith("retry_")]

    return {
        "parsed": parsed,
        "raw_text": raw_text,
        "raw_ok": bool(parsed),
        "attempts": llm_calls,
        "first_attempt_valid": llm_calls == 1,
        "retry_steps": retries,
        "total_ms": total_ms,
        "steps": steps,
    }


def score_output(company: dict, answers: dict, output: dict,
                 is_reassessment: bool, ex_id: str = "") -> dict:
    """Score an output against the training-validation rules. True == pass."""
    ex = {"id": ex_id,
          "input": {"company": company, "answers": answers},
          "output": output or {}}
    results = {
        "schema": not vs.check_schema(ex),
        "score": not vs.check_score(ex),
        "risk": not vs.check_risk_alignment(ex),
        "budget": not vs.check_budget_sanity(ex),
        "regulatory": not vs.check_regulatory(ex),
        "priority": not vs.check_priority_alignment(ex),
    }
    if is_reassessment:
        results.update({
            "reassessment_fields": not vs.check_reassessment_fields(ex),
            "carry_forward": not vs.check_carry_forward(ex),
            "score_delta": not vs.check_score_delta_consistency(ex),
            "progress": not vs.check_progress_structure(ex),
            "comparison": not vs.check_comparison_structure(ex),
        })
    return results


def completeness(output: dict, is_reassessment: bool) -> tuple[int, int]:
    """Return (present, required) count of required fields in an output."""
    required = [
        ("maturity_score", output.get("maturity_score") not in (None, "")),
    ]
    opps = output.get("opportunities", []) or []
    if isinstance(opps, list):
        for opp in opps:
            if not isinstance(opp, dict):
                continue
            for k in ("type", "title", "rationale", "impact",
                      "difficulty", "timeframe"):
                required.append((f"opp.{k}", opp.get(k) not in (None, "")))
            ep = opp.get("execution_plan") or {}
            for k in ("first_actions", "resources_needed",
                      "success_metric", "milestones"):
                required.append((f"opp.execution_plan.{k}",
                                 bool(ep.get(k))))
    steps = output.get("next_steps", []) or []
    if isinstance(steps, list):
        for step in steps:
            if not isinstance(step, dict):
                continue
            for k in ("action", "owner", "timeframe"):
                required.append((f"next_step.{k}", step.get(k) not in (None, "")))
    required.append(("key_weaknesses", bool(output.get("key_weaknesses"))))
    if is_reassessment:
        for k in ("score_delta", "progress", "comparison_to_previous"):
            required.append((k, output.get(k) not in (None, "", {}, [])))
    present = sum(1 for _, ok in required if ok)
    return present, len(required)


# ──────────────────────────────────────────────────────────────────────
# Statistics
# ──────────────────────────────────────────────────────────────────────

def wilson_ci(x: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = x / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided p-value for McNemar's test on discordant pairs b, c."""
    n = b + c
    if n == 0:
        return 1.0
    p_obs = math.comb(n, b) * (0.5 ** n)
    p = 0.0
    for k in range(n + 1):
        pk = math.comb(n, k) * (0.5 ** n)
        if pk <= p_obs + 1e-12:
            p += pk
    return p


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def report(results: dict, args) -> None:
    # Primary sample = one run (rep 0) per profile per model.
    primary = {k: v for k, v in results.items() if k[3] == 0}
    by_model = defaultdict(list)
    for key, r in primary.items():
        by_model[r["model"]].append(r)

    print("\n=== Reliability / latency (primary sample, rep 0) ===")
    rows = []
    for model in MODELS:
        rs = by_model.get(model, [])
        if not rs:
            continue
        n = len(rs)
        first = sum(1 for r in rs if r["first_attempt_valid"])
        retried = sum(1 for r in rs if not r["first_attempt_valid"])
        failed = sum(1 for r in rs if not r["raw_ok"])
        lats = [r["total_ms"] for r in rs]
        lo, hi = wilson_ci(first, n)
        rows.append({
            "model": model, "n": n, "first_attempt_valid": first,
            "first_attempt_rate": first / n, "retried": retried,
            "failed": failed, "mean_ms": sum(lats) / n, "max_ms": max(lats),
            "wilson": (lo, hi),
        })
        print(f"  {model}: {first}/{n} first-attempt ({first/n:.0%}), "
              f"{retried} re-prompted, {failed} failed | "
              f"latency mean={sum(lats)/n/1000:.0f}s max={max(lats)/1000:.0f}s | "
              f"Wilson95={lo:.2f}-{hi:.2f}")

    if len(rows) == 2:
        a, b = rows
        paired = defaultdict(dict)
        for (cell, fn, model, rep), r in primary.items():
            paired[cell][model] = r
        b_count = c_count = 0
        for cell, m in paired.items():
            if set(m) != set(MODELS):
                continue
            a_fail = not m[a["model"]]["first_attempt_valid"]
            b_fail = not m[b["model"]]["first_attempt_valid"]
            if a_fail and not b_fail:
                b_count += 1
            if not a_fail and b_fail:
                c_count += 1
        print(f"\n  McNemar (paired first-attempt, n={len(paired)}): discordant "
              f"gemma-fail/caforb-pass={b_count}, "
              f"gemma-pass/caforb-fail={c_count}, "
              f"p={mcnemar_exact(b_count, c_count):.3f}")

    print("\n=== Rule-level pass rates (primary sample, rep 0) ===")
    rules = ["schema", "score", "risk", "budget", "regulatory", "priority",
             "reassessment_fields", "carry_forward", "score_delta",
             "progress", "comparison"]
    for model in MODELS:
        rs = by_model.get(model, [])
        if not rs:
            continue
        scores = defaultdict(lambda: [0, 0])
        for r in rs:
            for rule, ok in r["rules"].items():
                scores[rule][1] += 1
                if ok:
                    scores[rule][0] += 1
        parts = [f"{rule}={p}/{t}" for rule, (p, t) in scores.items()
                 if rule in rules and t]
        print(f"  {model}: " + ", ".join(parts))

    print("\n=== Completeness (primary sample, rep 0) ===")
    for model in MODELS:
        rs = by_model.get(model, [])
        if not rs:
            continue
        fracs = [r["completeness"][0] / r["completeness"][1]
                 for r in rs if r["completeness"][1]]
        print(f"  {model}: {sum(fracs)/len(fracs):.1%} (n={len(fracs)})")

    print("\n=== Maturity scores + content length (primary sample, rep 0) ===")
    score_map = defaultdict(list)
    opp_map = defaultdict(list)
    weak_map = defaultdict(list)
    for model in MODELS:
        for r in by_model.get(model, []):
            p = r["parsed"] if isinstance(r["parsed"], dict) else {}
            if p.get("maturity_score") is not None:
                score_map[model].append(p["maturity_score"])
            opp_map[model].append(len(p.get("opportunities", []) or []))
            weak_map[model].append(len(p.get("key_weaknesses", []) or []))
        s = score_map[model]
        if s:
            print(f"  {model}: score mean={statistics.mean(s):.2f} "
                  f"median={statistics.median(s):.2f} "
                  f"min={min(s)} max={max(s)} (n={len(s)})")
            print(f"           opportunities mean={statistics.mean(opp_map[model]):.2f} | "
                  f"weaknesses mean={statistics.mean(weak_map[model]):.2f}")

    paired = defaultdict(dict)
    for (cell, fn, model, rep), r in primary.items():
        paired[cell][model] = r
    diffs = []
    for cell, m in paired.items():
        if set(m) != set(MODELS):
            continue
        a = (m[MODELS[0]]["parsed"].get("maturity_score")
             if isinstance(m[MODELS[0]]["parsed"], dict) else None)
        b = (m[MODELS[1]]["parsed"].get("maturity_score")
             if isinstance(m[MODELS[1]]["parsed"], dict) else None)
        if a is not None and b is not None:
            diffs.append((b - a, cell))
    if diffs:
        mean_diff = statistics.mean(d for d, _ in diffs)
        n_pos = sum(1 for d, _ in diffs if d > 0)
        n_neg = sum(1 for d, _ in diffs if d < 0)
        n_tie = len(diffs) - n_pos - n_neg
        print(f"  paired score diff (caforb - gemma): mean={mean_diff:+.2f} | "
              f"caforb higher on {n_pos}, lower on {n_neg}, tied on {n_tie}")

    print("\n=== Failure detail (primary sample, rep 0) ===")
    for model in MODELS:
        for rule in ("risk", "priority", "regulatory"):
            fails = [(cell, fn) for (cell, fn, m, rep), r in results.items()
                     if rep == 0 and m == model and not r["rules"].get(rule, True)]
            if fails:
                print(f"  {model} {rule} failed ({len(fails)}): {fails}")

    # Repetition stability for the subset (all reps).
    print("\n=== Repetition stability (subset profiles) ===")
    rep_groups = defaultdict(list)
    for (cell, fn, model, rep), r in results.items():
        if rep > 0:
            rep_groups[(cell, fn)].append(r)
    stable = 0
    unstable = []
    for (cell, fn), rs in rep_groups.items():
        if not rs:
            continue
        # compare rep>0 results against rep 0 first-attempt outcome
        base = {m: results[(cell, fn, m, 0)]["first_attempt_valid"]
                for m in MODELS if (cell, fn, m, 0) in results}
        consistent = all(
            r["first_attempt_valid"] == base[r["model"]]
            for r in rs
        )
        if consistent:
            stable += 1
        else:
            unstable.append((cell, fn))
    print(f"  profiles with identical first-attempt outcome across reps: "
          f"{stable}/{len(rep_groups)}")
    if unstable:
        print("  inconsistent:", unstable)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--dry-run", action="store_true",
                    help="print the selected profiles and exit")
    ap.add_argument("--mock", action="store_true",
                    help="score the stored gold outputs instead of calling models")
    ap.add_argument("--reps", type=int, default=3,
                    help="repetitions for the subset")
    ap.add_argument("--subset-size", type=int, default=6,
                    help="number of profiles to repeat")
    ap.add_argument("--out", default=str(BASE_DIR / "final" / "ab_results.json"))
    args = ap.parse_args()
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    profiles = select_profiles()
    print(f"Selected {len(profiles)} held-out profiles (one per cell):")
    for cell, fn, is_re in profiles:
        print(f"  {cell[0]:<13} {cell[1]:<15} {cell[2]:<6} {fn}  "
              f"{'REASSESS' if is_re else 'first'}")

    # Deterministic 6-profile repetition subset spanning all three risks and
    # four priorities (two cells per risk: one low + one high regulation).
    subset_cells = {
        ("conservative", "growth", "low"),
        ("conservative", "efficiency", "high"),
        ("balanced", "market_defense", "low"),
        ("balanced", "diversification", "high"),
        ("bold", "growth", "low"),
        ("bold", "efficiency", "high"),
    }
    subset_fns = {fn for cell, fn, _ in profiles if cell in subset_cells}
    print(f"Repetition subset ({len(subset_fns)} profiles): "
          f"{sorted(subset_fns)}")

    if args.dry_run:
        return

    results = {}
    profile_keys = {fn: cell for cell, fn, _ in profiles}

    for model in models:
        for cell, fn, is_re in profiles:
            d = json.loads((RAW_DIR / fn).read_text(encoding="utf-8"))
            company = d["input"]["company"]
            answers = d["input"]["answers"]
            history = build_history(d) if is_re else None

            for rep in range(args.reps if fn in subset_fns else 1):
                if args.mock:
                    run = {
                        "parsed": d["output"],
                        "raw_ok": True,
                        "attempts": 1,
                        "first_attempt_valid": True,
                        "retry_steps": [],
                        "total_ms": 0,
                    }
                else:
                    run = run_generation(company, answers, model, history)
                run["model"] = model
                run["profile_key"] = cell
                run["profile_file"] = fn
                run["rep"] = rep
                run["rules"] = score_output(company, answers,
                                            run["parsed"], is_re, ex_id=fn)
                run["completeness"] = completeness(run["parsed"], is_re)
                key = (cell, fn, model, rep)
                results[key] = run
                status = ("PASS" if run["first_attempt_valid"] else "RETRY")
                if not run["raw_ok"]:
                    status = "FAIL"
                print(f"  [{model}] {fn} rep{rep} {status} "
                      f"attempts={run['attempts']} "
                      f"latency={run['total_ms']/1000:.0f}s")

    report(results, args)

    out = args.out
    if out:
        serial = {}
        runs_dir = BASE_DIR / "final" / "ab_runs"
        runs_dir.mkdir(exist_ok=True)
        for (cell, fn, model, rep), r in results.items():
            parsed = r["parsed"] if isinstance(r["parsed"], dict) else {}
            serial[f"{cell}|{fn}|{model}|r{rep}"] = {
                "model": model,
                "first_attempt_valid": r["first_attempt_valid"],
                "attempts": r["attempts"],
                "raw_ok": r["raw_ok"],
                "total_ms": r["total_ms"],
                "retry_steps": r["retry_steps"],
                "maturity_score": parsed.get("maturity_score"),
                "n_opportunities": len(parsed.get("opportunities", []) or []),
                "n_weaknesses": len(parsed.get("key_weaknesses", []) or []),
                "rules": r["rules"],
                "completeness_present": r["completeness"][0],
                "completeness_total": r["completeness"][1],
            }
            safe_model = model.replace(":", "-")
            (runs_dir / f"{fn}_{safe_model}_r{rep}.json").write_text(
                json.dumps({
                    "cell": list(cell),
                    "file": fn,
                    "model": model,
                    "rep": rep,
                    "maturity_score": parsed.get("maturity_score"),
                    "parsed_output": parsed,
                    "raw_text": r.get("raw_text"),
                    "steps": r.get("steps", []),
                    "retry_steps": r["retry_steps"],
                    "total_ms": r["total_ms"],
                    "attempts": r["attempts"],
                    "rules": r["rules"],
                    "completeness": r["completeness"],
                }, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        Path(out).write_text(json.dumps(serial, indent=2), encoding="utf-8")
        print(f"\nWrote {out} and {len(serial)} per-run dumps to {runs_dir}")


if __name__ == "__main__":
    main()
