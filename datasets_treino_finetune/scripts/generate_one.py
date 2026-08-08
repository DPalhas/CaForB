#!/usr/bin/env python3
"""
generate_one.py — One-shot JSON generation with classical heuristic validation.

Each invocation generates exactly one training example:
  1. Pre-determined structured fields are LOCKED (from raw_inputs.json)
  2. LLM enriches free-text fields and generates the output (innovation analysis)
  3. Locked fields are validated for tampering; violators fed back for correction
  4. Valid output is saved to raw/XXXX.json

Usage:
    python scripts/generate_one.py 42
    python scripts/generate_one.py 42 --model gemma4:e2b-it-qat --gpu-layers -1
"""

import json
import re
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

import ollama

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "raw_inputs.json"
OUTPUT_DIR = BASE_DIR / "raw"

# ──────────────────────────────────────────────────────────────────────
# Field domains
# ──────────────────────────────────────────────────────────────────────

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
RISK_LEVELS = ["low", "medium", "high"]
INNOVATION_PROCESSES = ["none", "informal", "partial", "formal"]
CUSTOMER_FEEDBACKS = ["no_formal_process", "informal_conversations", "surveys_nps", "dedicated_research"]
STRATEGIC_PRIORITIES = ["growth", "efficiency", "market_defense", "diversification"]
RISK_APPETITES = ["conservative", "balanced", "bold"]
TIME_HORIZONS = ["short", "medium", "long"]
DECISION_MAKINGS = ["owner_alone", "small_leadership_team", "formal_committee", "varies_by_project"]
DIGITAL_MATURITIES = ["1", "2", "3", "4"]
REVENUE_RANGES = ["under_1m", "1m_to_10m", "10m_to_50m", "over_50m"]
ALL_BARRIERS = ["budget", "talent", "process", "culture", "time", "strategy"]

# Fields that the LLM MUST return exactly as provided (locked)
LOCKED_FIELDS = [
    "sector", "size", "regulatoryEnvironment", "innovationProcess",
    "customerFeedback", "strategicPriority", "timeHorizon", "riskAppetite",
    "digitalMaturity", "revenueRange", "budgetPercentage", "decisionMaking",
    "mainBarrier", "competitivePressure",
]

# Fields the LLM can expand/enrich (free-text)
FREE_TEXT_FIELDS = [
    "companyName", "companyDescription", "pastInitiatives",
    "strategicGoals", "teamSize", "additionalContext",
]


# ──────────────────────────────────────────────────────────────────────
# Load survey input
# ──────────────────────────────────────────────────────────────────────

def load_survey(index: int) -> dict:
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        all_examples = json.load(f)
    if index < 0 or index >= len(all_examples):
        raise IndexError(f"Index {index} out of range (0..{len(all_examples)-1})")
    return all_examples[index]


# ──────────────────────────────────────────────────────────────────────
# Prompt — locked fields + free-text enrichment + output generation
# ──────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a data generator for fine-tuning a corporate innovation assessment AI.

You will receive a pre-determined corporate survey (locked fields + template text).
Your job: enrich the template text fields with realistic industry-specific detail, then
generate a complete innovation analysis.

LOCKED FIELDS: Do NOT change these values. Return them exactly as provided.
FREE-TEXT FIELDS: Expand these with 2-3 sentences of realistic, industry-specific detail.
OUTPUT: Generate a complete innovation analysis (score, opportunities, next steps, weaknesses).

Output MUST be this exact structure:
{
  "company": {
    "companyName": "<enriched from template>",
    "sector": "<LOCKED — dont change>",
    "size": "<LOCKED — dont change>"
  },
  "answers": {
    "regulatoryEnvironment": "<LOCKED>",
    "companyDescription": "<2-3 sentences, sector-specific>",
    "innovationProcess": "<LOCKED>",
    "pastInitiatives": "<2-3 sentences, realistic>",
    "customerFeedback": "<LOCKED>",
    "strategicGoals": "<2-3 sentences aligned with priority>",
    "strategicPriority": "<LOCKED>",
    "timeHorizon": "<LOCKED>",
    "riskAppetite": "<LOCKED>",
    "teamSize": "<1-2 sentences>",
    "digitalMaturity": "<LOCKED>",
    "revenueRange": "<LOCKED>",
    "budgetPercentage": "<LOCKED — number>",
    "decisionMaking": "<LOCKED>",
    "mainBarrier": ["<LOCKED — array>"],
    "competitivePressure": "<LOCKED>",
    "additionalContext": "<0-2 sentences or empty>"
  },
  "output": {
    "maturity_score": <float 0-10>,
    "opportunities": [
      {
        "type": "incremental | radical",
        "title": "<string>",
        "rationale": "<2-3 sentences>",
        "execution_plan": {
          "first_actions": ["<2-3 specific steps>"],
          "resources_needed": ["<2-3 resources/costs>"],
          "success_metric": "<measurable KPI with target>",
          "milestones": ["<2-3 timed milestones>"]
        },
        "impact": "low | medium | high",
        "difficulty": "low | medium | high",
        "timeframe": "<string>"
      }
    ],
    "next_steps": [
      {
        "action": "<specific action>",
        "owner": "<role>",
        "timeframe": "<e.g. Within 2 weeks>"
      }
    ],
    "key_weaknesses": ["<2-4 specific weaknesses>"]
  }
}

RULES:
- Generate 2-4 opportunities (Conservative=all incremental, Bold=at least one radical)
- MUST include key_weaknesses (2-4 items) and next_steps (2-3 items)
- Execution plans must stay within the company's estimated budget
- All locked fields MUST be returned unchanged
- RESPOND WITH ONLY THE RAW JSON. No markdown. No explanation. No backticks."""


def build_prompt(fields: dict, feedback: str = "") -> str:
    locked_block = "\n".join(
        f"  {k}: {json.dumps(fields.get(k, ''))}"
        for k in LOCKED_FIELDS
    )
    templates_block = "\n".join(
        f"  {k}: {json.dumps(fields.get(k, '')) if fields.get(k) else '(empty — invent)'}"
        for k in FREE_TEXT_FIELDS
    )

    combo = (
        f"{fields.get('riskAppetite','')}|{fields.get('strategicPriority','')}"
        f"|{fields.get('regulatoryEnvironment','')}"
    )

    base = (
        f"Generate a training example for innovation assessment.\n\n"
        f"Constraint combo: {combo}\n\n"
        f"--- LOCKED FIELDS (do NOT change) ---\n{locked_block}\n\n"
        f"--- TEMPLATE TEXT (enrich with 2-3 realistic sentences) ---\n{templates_block}\n\n"
        f"Enrich free-text fields with sector-appropriate realism. "
        f"Generate a full innovation analysis. "
        f"Conservative risk = all incremental ops. Bold = at least one radical."
    )

    if feedback:
        base += f"\n\nPREVIOUS ATTEMPT FAILED:\n{feedback}\n\nFix ALL violations and regenerate."

    return base


# ──────────────────────────────────────────────────────────────────────
# Validation — checks only that locked fields weren't altered
# ──────────────────────────────────────────────────────────────────────

def validate_locked(expected: dict, llm_company: dict, llm_answers: dict) -> list[str]:
    """Verify LLM didn't change any locked fields. Returns violation messages."""
    violations = []

    for field in LOCKED_FIELDS:
        expected_val = expected.get(field)
        if field in ("sector", "size"):
            actual = llm_company.get(field)
        else:
            actual = llm_answers.get(field)

        if actual is None:
            violations.append(f"LOCKED field '{field}' is missing from LLM output")
            continue

        if isinstance(expected_val, list):
            if sorted(actual) != sorted(expected_val):
                violations.append(
                    f"LOCKED field '{field}' was altered: expected {expected_val}, got {actual}"
                )
        elif isinstance(expected_val, (int, float)):
            if int(actual) != int(expected_val):
                violations.append(
                    f"LOCKED field '{field}' was altered: expected {expected_val}, got {actual}"
                )
        else:
            if str(actual) != str(expected_val):
                violations.append(
                    f"LOCKED field '{field}' was altered: expected '{expected_val}', got '{actual}'"
                )

    return violations


# ──────────────────────────────────────────────────────────────────────
# JSON extraction
# ──────────────────────────────────────────────────────────────────────

def extract_json(text: str) -> dict:
    for attempt in [
        lambda t: json.loads(t),
        lambda t: json.loads(re.search(r'\{.*\}', t, re.DOTALL).group()) if re.search(r'\{.*\}', t, re.DOTALL) else {},
        lambda t: json.loads(re.sub(r'\}\s*$', ']}', t.rstrip())),
        lambda t: json.loads(re.sub(r'(\s*\]?\s*)\}$', '\n  ]\n}', t.rstrip())),
    ]:
        try:
            result = attempt(text)
            if result and "company" in result:
                return result
        except (json.JSONDecodeError, AttributeError):
            continue
    return {}


# ──────────────────────────────────────────────────────────────────────
# LLM call
# ──────────────────────────────────────────────────────────────────────

def call_llm(fields: dict, feedback: str, model: str, gpu_layers: int, num_predict: int) -> str:
    prompt = build_prompt(fields, feedback)
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={
            "num_predict": num_predict,
            "num_gpu": gpu_layers,
            "temperature": 0.8,
        },
    )
    return response.message.content


# ──────────────────────────────────────────────────────────────────────
# Main one-shot generator
# ──────────────────────────────────────────────────────────────────────

def generate_one(
    index: int,
    model: str,
    gpu_layers: int,
    num_predict: int = 12288,
    max_retries: int = 5,
) -> str | None:
    survey = load_survey(index)
    ex_id = survey["id"]
    fields = survey["fields"]
    combo_id = survey["combo_id"]

    out_path = OUTPUT_DIR / f"{ex_id}.json"
    if out_path.exists():
        print(f"  {ex_id} already exists, skipping")
        return None

    print(f"  [{index}] {ex_id}  {combo_id}")
    feedback = ""
    start = time.time()

    for attempt in range(1, max_retries + 1):
        raw_text = call_llm(fields, feedback, model, gpu_layers, num_predict)
        parsed = extract_json(raw_text)

        if not parsed or "company" not in parsed or "answers" not in parsed:
            feedback = (
                "ERROR: Output was not valid JSON or missing 'company'/'answers' keys. "
                "Respond with ONLY the JSON object, no markdown, no backticks, no explanation."
            )
            print(f"    Attempt {attempt}: unparseable JSON")
            continue

        llm_company = parsed.get("company", {})
        llm_answers = parsed.get("answers", {})
        llm_output = parsed.get("output", {})

        violations = validate_locked(fields, llm_company, llm_answers)

        if violations:
            feedback = "LOCKED FIELDS WERE ALTERED:\n" + "\n".join(f"  - {v}" for v in violations)
            feedback += "\n\nAll locked fields from the input MUST be returned unchanged."
            print(f"    Attempt {attempt}: {len(violations)} locked-field violation(s)")
            for v in violations[:3]:
                print(f"      - {v}")
            if len(violations) > 3:
                print(f"      ... and {len(violations)-3} more")
            continue

        duration_ms = int((time.time() - start) * 1000)

        result = {
            "id": ex_id,
            "version": 1,
            "split": "train",
            "metadata": {
                "sector": fields["sector"],
                "size": fields["size"],
                "regulatory_environment": fields["regulatoryEnvironment"],
                "risk_appetite": fields["riskAppetite"],
                "strategic_priority": fields["strategicPriority"],
                "competitive_pressure": fields["competitivePressure"],
                "reviewed": False,
                "source": f"{model}_synthetic",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "duration_ms": duration_ms,
                "attempts": attempt,
            },
            "instruction": (
                "You are a strategic corporate innovation advisor. "
                "Analyse the company profile and survey responses, then respond ONLY with "
                "a valid JSON object containing maturity_score, opportunities, next_steps, "
                "and key_weaknesses."
            ),
            "input": {
                "company": {
                    "name": llm_company.get("companyName", fields.get("companyName", "")),
                    "sector": fields["sector"],
                    "size": fields["size"],
                },
                "answers": {
                    # Start with ALL original fields as defaults
                    **{k: v for k, v in fields.items() if k not in ("companyName", "sector", "size")},
                    # Override with LLM's enriched free-text fields
                    **{k: v for k, v in llm_answers.items() if k not in LOCKED_FIELDS and k not in ("sector", "size")},
                    # Ensure locked fields are correct (belt-and-suspenders)
                    **{k: fields[k] for k in LOCKED_FIELDS},
                },
            },
            "output": llm_output,
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"    OK ({duration_ms}ms, {attempt} attempt(s))")
        return ex_id

    print(f"    FAILED after {max_retries} attempts")
    return None


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="One-shot training example generation.")
    parser.add_argument("index", type=int, help="Index into raw_inputs.json (0-based)")
    parser.add_argument("--model", default="gemma4:e2b-it-qat", help="Ollama model name")
    parser.add_argument("--gpu-layers", type=int, default=-1, help="GPU layers (-1=all, 0=CPU)")
    parser.add_argument("--num-predict", type=int, default=12288, help="Max output tokens")
    parser.add_argument("--retries", type=int, default=5, help="Max retry attempts")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Model: {args.model}")
    print(f"Device: {'GPU' if args.gpu_layers != 0 else 'CPU'}")
    print(f"Max retries: {args.retries}")

    result = generate_one(args.index, args.model, args.gpu_layers, args.num_predict, args.retries)

    if result:
        print(f"\nGenerated: raw/{result}.json")
    else:
        print(f"\nFailed to generate valid JSON")
        sys.exit(1)


if __name__ == "__main__":
    main()
