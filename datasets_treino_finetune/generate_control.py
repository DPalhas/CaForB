#!/usr/bin/env python3
"""
generate_control.py — Generate the generic-control outputs for the expert evaluation.

For each of the six selected profiles, runs gemma4:12B with NO company
characteristics (a generic "Company" and empty answers), producing standard
innovation guidance in the same JSON contract as the tailored runs. This is
the "C" (generic) condition that experts rate alongside A (caforb-v1, tailored)
and B (gemma4:12B, tailored) to test whether tailoring adds perceived value
over generic guidance (RQ2_H2).

Usage:
    python generate_control.py --dry-run   # print the 6 profiles and exit
    python generate_control.py --mock      # write placeholder controls (no Ollama)
    python generate_control.py             # full run (Ollama required)
"""

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FINAL_DIR = BASE_DIR / "final"

# Make the CaForB app importable so the control reuses the exact runtime
# generation loop (same prompt builders and self-correcting loop as the A/B runs).
sys.path.insert(0, str(BASE_DIR.parent))          # CaForB root -> core.services

from core.services.llm_services import (          # noqa: E402
    generate_innovation_insight,
    _extract_json,
)

PROFILES = ["0028.json", "0045.json", "0047.json",
            "0100.json", "0197.json", "0395.json"]
MODEL = "gemma4:12B"

# The generic company: no name beyond "Company", empty sector/size, empty
# answers, so no risk-appetite, priority or regulatory constraints are injected.
GENERIC_COMPANY = {"name": "Company", "sector": "", "size": ""}
GENERIC_ANSWERS = {}


def run_control(model: str = MODEL) -> dict:
    """Run one generic-control generation; return parsed + raw + metrics."""
    steps = []

    def trace_cb(step_name, inp, out, duration_ms):
        steps.append((step_name, out, duration_ms))

    raw_text, total_ms = generate_innovation_insight(
        GENERIC_COMPANY, GENERIC_ANSWERS, model=model, trace_cb=trace_cb
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print the 6 profiles and exit")
    ap.add_argument("--mock", action="store_true",
                    help="write placeholder controls without calling Ollama")
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()

    print(f"Generating generic-control outputs for {len(PROFILES)} profiles:")
    for fn in PROFILES:
        print(f"  {fn}")

    if args.dry_run:
        return

    out_dir = FINAL_DIR / "ab_runs" / "control"
    out_dir.mkdir(parents=True, exist_ok=True)

    for fn in PROFILES:
        if args.mock:
            run = {
                "parsed": {},
                "raw_text": "",
                "raw_ok": True,
                "attempts": 1,
                "first_attempt_valid": True,
                "retry_steps": [],
                "total_ms": 0,
                "steps": [],
            }
        else:
            run = run_control(args.model)

        parsed = run["parsed"] if isinstance(run["parsed"], dict) else {}
        dump = {
            "profile": fn,
            "condition": "C (generic control, no company characteristics)",
            "model": args.model,
            "maturity_score": parsed.get("maturity_score"),
            "parsed_output": parsed,
            "raw_text": run["raw_text"],
            "steps": run["steps"],
            "retry_steps": run["retry_steps"],
            "total_ms": run["total_ms"],
            "attempts": run["attempts"],
            "raw_ok": run["raw_ok"],
        }
        (out_dir / f"{fn}_control.json").write_text(
            json.dumps(dump, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        status = "PASS" if run["first_attempt_valid"] else "RETRY"
        if not run["raw_ok"]:
            status = "FAIL"
        print(f"  [{args.model}] {fn} {status} attempts={run['attempts']} "
              f"latency={run['total_ms']/1000:.0f}s")

    print(f"\nWrote {len(PROFILES)} control outputs to {out_dir}")


if __name__ == "__main__":
    main()
