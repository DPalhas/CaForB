#!/usr/bin/env python3
"""
build_expert_pack.py — Assemble the expert-evaluation materials.

For each of the six selected profiles, builds a folder containing the company
profile and the three outputs (fine-tuned caforb-v1, baseline gemma4:12B, and
the generic no-profile control), rendered as readable text. The three outputs
are written as A.txt / B.txt / C.txt with the A/B/C letters randomly permuted
per profile, so an evaluator cannot infer the condition from the letter. The
researcher-only key (KEY.txt) records the true mapping.

Usage:
    python build_expert_pack.py --dry-run      # print the mapping, write nothing
    python build_expert_pack.py               # write expert_eval/
    python build_expert_pack.py --seed 7      # different random assignment
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"
RUNS_DIR = BASE_DIR / "final" / "ab_runs"
CONTROL_DIR = RUNS_DIR / "control"

# Make the CaForB app importable so the profile rendering reuses the exact
# company-data formatting the models were shown.
sys.path.insert(0, str(BASE_DIR.parent))          # CaForB root -> core.services

from core.services.llm_services import _format_company_data  # noqa: E402

PROFILES = [
    ("0028.json", "Strato"),
    ("0045.json", "Forge Analytics"),
    ("0047.json", "Core Technologies"),
    ("0100.json", "Lumina Consulting"),
    ("0197.json", "Vertex Analytics"),
    ("0395.json", "Orbit Innovations"),
]

CONDITIONS = ["finetune", "baseline", "generic"]
CONDITION_LABEL = {
    "finetune": "caforb-v1 (fine-tuned, tailored)",
    "baseline": "gemma4:12B (baseline, tailored)",
    "generic": "gemma4:12B, no company profile (generic control)",
}


def load_parsed(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    out = d.get("parsed_output") or d.get("parsed") or {}
    return out if isinstance(out, dict) else {}


def render_output(parsed: dict) -> str:
    """Render a parsed assessment output as readable text for an expert."""
    if not parsed:
        return "(no output — generation failed)"

    lines = []
    ms = parsed.get("maturity_score")
    if ms is not None:
        lines.append(f"Maturity Score: {ms} / 10")
        lines.append("")

    opps = parsed.get("opportunities") or []
    if isinstance(opps, list) and opps:
        lines.append("OPPORTUNITIES")
        lines.append("-" * 40)
        for i, o in enumerate(opps, 1):
            if not isinstance(o, dict):
                continue
            lines.append(f"{i}. [{str(o.get('type', '?')).capitalize()}] {o.get('title', '(untitled)')}")
            if o.get("rationale"):
                lines.append(f"   Rationale: {o['rationale']}")
            meta = [f"{k.capitalize()}: {o[k]}" for k in ("impact", "difficulty", "timeframe") if o.get(k)]
            if meta:
                lines.append("   " + " | ".join(meta))
            ep = o.get("execution_plan")
            if isinstance(ep, dict):
                for label, key in (("First actions", "first_actions"),
                                   ("Resources needed", "resources_needed")):
                    vals = ep.get(key) or []
                    if vals:
                        lines.append(f"   {label}:")
                        for v in vals:
                            lines.append(f"     • {v}")
                if ep.get("success_metric"):
                    lines.append(f"   Success metric: {ep['success_metric']}")
                if ep.get("milestones"):
                    lines.append("   Milestones:")
                    for m in ep["milestones"]:
                        lines.append(f"     • {m}")
            lines.append("")

    ns = parsed.get("next_steps") or []
    if isinstance(ns, list) and ns:
        lines.append("NEXT STEPS")
        lines.append("-" * 40)
        for i, s in enumerate(ns, 1):
            if not isinstance(s, dict):
                continue
            parts = [s.get("action", "")]
            if s.get("owner") or s.get("timeframe"):
                parts.append(f"Owner: {s.get('owner', '')}; Timeframe: {s.get('timeframe', '')}")
            lines.append(f"{i}. {' — '.join(p for p in parts if p)}")
        lines.append("")

    kw = parsed.get("key_weaknesses") or []
    if isinstance(kw, list) and kw:
        lines.append("KEY WEAKNESSES")
        lines.append("-" * 40)
        for w in kw:
            lines.append(f"• {w}")
        lines.append("")

    return "\n".join(lines).strip()


def folder_name(fn: str, name: str) -> str:
    stem = fn[:-5]  # strip ".json"
    safe = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return f"{stem}_{safe}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print the mapping, write nothing")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", default=str(BASE_DIR / "expert_eval"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    out_dir = Path(args.out_dir)

    key_lines = [
        "RESEARCHER KEY — do not share with evaluators",
        "The letters A, B and C are randomly permuted per profile.",
        "",
        "Condition abbreviations:",
    ]
    for cond in CONDITIONS:
        key_lines.append(f"  {cond:<9} = {CONDITION_LABEL[cond]}")
    key_lines.append("")

    rows = []
    for fn, name in PROFILES:
        raw = json.loads((RAW_DIR / fn).read_text(encoding="utf-8"))
        company = raw["input"]["company"]
        answers = raw["input"]["answers"]

        content = {
            "finetune": load_parsed(RUNS_DIR / f"{fn}_caforb-v1_r0.json"),
            "baseline": load_parsed(RUNS_DIR / f"{fn}_gemma4-12B_r0.json"),
            "generic": load_parsed(CONTROL_DIR / f"{fn}_control.json"),
        }

        labels = ["A", "B", "C"]
        conds = CONDITIONS[:]
        rng.shuffle(conds)
        mapping = dict(zip(labels, conds))  # label -> condition

        folder = out_dir / folder_name(fn, name)
        rows.append((fn, name, mapping))

        if args.dry_run:
            continue

        folder.mkdir(parents=True, exist_ok=True)
        (folder / "profile.txt").write_text(
            "COMPANY PROFILE\n\n" + _format_company_data(company, answers),
            encoding="utf-8",
        )
        for label in labels:
            cond = mapping[label]
            (folder / f"{label}.txt").write_text(render_output(content[cond]), encoding="utf-8")

    for fn, name, mapping in rows:
        key_lines.append(
            f"{fn} — {name:<20}: A={mapping['A']:<9} B={mapping['B']:<9} C={mapping['C']}"
        )

    print("\n".join(key_lines))

    if args.dry_run:
        print("\n(dry run — nothing written)")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "KEY.txt").write_text("\n".join(key_lines) + "\n", encoding="utf-8")
    print(f"\nWrote {len(PROFILES)} profile folders + KEY.txt to {out_dir}")


if __name__ == "__main__":
    main()
