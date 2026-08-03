#!/usr/bin/env python3
"""
generate_one.py — One-shot JSON generation with classical heuristic validation.

Each invocation generates exactly one training example:
  1. LLM produces a complete survey JSON (input + output) in one prompt
  2. Non-free-text fields are validated with classical heuristics
  3. Violations are fed back to the LLM for correction (up to N retries)
  4. Valid output is saved to raw/XXXX.json

Usage:
    python scripts/generate_one.py 42                    # Generate example at index 42
    python scripts/generate_one.py 42 --model gemma4:e2b-it-qat
    python scripts/generate_one.py 42 --retries 5 --gpu-layers -1
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
# Field domains for validation
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
RISK_APPETITES = ["conservative", "balanced", "bold"]
STRATEGIC_PRIORITIES = ["growth", "efficiency", "market_defense", "diversification"]
INNOVATION_PROCESSES = ["none", "informal", "partial", "formal"]
CUSTOMER_FEEDBACKS = ["no_formal_process", "informal_conversations", "surveys_nps", "dedicated_research"]
TIME_HORIZONS = ["short", "medium", "long"]
DECISION_MAKINGS = ["owner_alone", "small_leadership_team", "formal_committee", "varies_by_project"]
DIGITAL_MATURITIES = ["1", "2", "3", "4"]
REVENUE_RANGES = ["under_1m", "1m_to_10m", "10m_to_50m", "over_50m"]
ALL_BARRIERS = ["budget", "talent", "process", "culture", "time", "strategy"]

USED_IDS_FILE = BASE_DIR / "used_ids.txt"

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
# One-shot prompt
# ──────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a data generator for fine-tuning a corporate innovation assessment AI.

Produce ONE JSON with a corporate survey AND its corresponding innovation analysis.

EXACT OUTPUT STRUCTURE:
{
  "company": {
    "companyName": "string",
    "sector": "EXACT match from provided list",
    "size": "Micro | Small | Medium | Large"
  },
  "answers": {
    "regulatoryEnvironment": "low | medium | high",
    "companyDescription": "3-4 sentences, industry-specific",
    "innovationProcess": "none | informal | partial | formal",
    "pastInitiatives": "2-3 sentences, realistic",
    "customerFeedback": "no_formal_process | informal_conversations | surveys_nps | dedicated_research",
    "strategicGoals": "2-3 sentences matching the strategic priority",
    "strategicPriority": "growth | efficiency | market_defense | diversification",
    "timeHorizon": "short | medium | long",
    "riskAppetite": "conservative | balanced | bold",
    "teamSize": "1-2 sentences about team",
    "digitalMaturity": "1 | 2 | 3 | 4",
    "revenueRange": "under_1m | 1m_to_10m | 10m_to_50m | over_50m",
    "budgetPercentage": "integer 0-30",
    "decisionMaking": "owner_alone | small_leadership_team | formal_committee | varies_by_project",
    "mainBarrier": ["array of 1-4 from: budget | talent | process | culture | time | strategy"],
    "competitivePressure": "low | medium | high",
    "additionalContext": "0-2 sentences or empty string"
  },
  "output": {
    "maturity_score": <float 0-10>,
    "opportunities": [
      {
        "type": "incremental | radical",
        "title": "<string>",
        "rationale": "<2-3 sentences linking to company context>",
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

CRITICAL RULES:
- Generate 2-4 opportunities (NOT just 1). Balanced risk = mix of types. Bold = at least one radical. Conservative = all incremental.
- MUST include key_weaknesses array (2-4 items). Never omit this field.
- MUST include 2-3 next_steps.
- budgetPercentage: conservative 2-6%, balanced 5-15%, bold 12-25%
- revenueRange must match size: Micro->under_1m, Small->1m_to_10m, Medium->10m_to_50m, Large->over_50m
- decisionMaking must match size: Micro->owner_alone, Large->formal_committee or varies_by_project
- digitalMaturity consistent with innovationProcess + size
- Opportunities must align with strategic priority and risk appetite
- Execution plan resources must stay within estimated budget

RESPOND WITH ONLY THE RAW JSON. No markdown backticks. No explanation text."""


def build_prompt(combo_id: str, feedback: str = "") -> str:
    sectors_str = ", ".join(SECTORS)
    risk, prio, reg = combo_id.split("|")
    base = (
        f"Generate a complete training example for innovation assessment.\n"
        f"Constraint: riskAppetite={risk}, strategicPriority={prio}, regulatoryEnvironment={reg}.\n"
        f"IMPORTANT: Use only these sectors: {sectors_str}\n"
        f"decisionMaking: {', '.join(DECISION_MAKINGS)}\n"
        f"Generate 2-4 opportunities. Include key_weaknesses. Vary the company realistically."
    )
    if feedback:
        base += f"\n\nPREVIOUS ATTEMPT FAILED VALIDATION:\n{feedback}\n\nPlease fix ALL violations and regenerate."
    return base


# ──────────────────────────────────────────────────────────────────────
# Field validators
# ──────────────────────────────────────────────────────────────────────

class ValidationError(Exception):
    pass


def validate_enum(value: Any, domain: list[str], field: str) -> None:
    if value not in domain:
        raise ValidationError(f"{field}='{value}' is not in {domain}")


def validate_int_range(value: Any, lo: int, hi: int, field: str) -> None:
    if not isinstance(value, (int, float)) or value < lo or value > hi:
        raise ValidationError(f"{field}={value} must be integer {lo}-{hi}")
    if isinstance(value, float) and not value.is_integer():
        raise ValidationError(f"{field}={value} must be integer, got float")


def validate_barriers(value: Any) -> None:
    if not isinstance(value, list):
        raise ValidationError(f"mainBarrier must be an array, got {type(value)}")
    for b in value:
        if b not in ALL_BARRIERS:
            raise ValidationError(f"mainBarrier contains invalid value '{b}'")


def validate_fields(fields: dict) -> list[str]:
    """Run all field-level validations. Returns list of violation messages (empty = valid)."""
    violations = []

    checks = [
        ("regulatoryEnvironment", RISK_LEVELS),
        ("innovationProcess", INNOVATION_PROCESSES),
        ("customerFeedback", CUSTOMER_FEEDBACKS),
        ("strategicPriority", STRATEGIC_PRIORITIES),
        ("timeHorizon", TIME_HORIZONS),
        ("riskAppetite", RISK_APPETITES),
        ("revenueRange", REVENUE_RANGES),
        ("decisionMaking", DECISION_MAKINGS),
        ("competitivePressure", RISK_LEVELS),
    ]

    for field, domain in checks:
        try:
            validate_enum(fields.get(field), domain, field)
        except ValidationError as e:
            violations.append(str(e))

    dm = fields.get("digitalMaturity")
    try:
        validate_enum(str(dm) if dm is not None else None, DIGITAL_MATURITIES, "digitalMaturity")
    except ValidationError as e:
        violations.append(str(e))

    bp = fields.get("budgetPercentage")
    try:
        validate_int_range(int(bp) if bp is not None else -1, 0, 30, "budgetPercentage")
    except (ValueError, TypeError, ValidationError) as e:
        violations.append(f"budgetPercentage={bp}: {e}")

    try:
        validate_barriers(fields.get("mainBarrier"))
    except ValidationError as e:
        violations.append(str(e))

    return violations


# ──────────────────────────────────────────────────────────────────────
# Cross-field heuristic validators
# ──────────────────────────────────────────────────────────────────────

def validate_correlations(fields: dict) -> list[str]:
    """Run cross-field consistency checks. Returns list of violation messages."""
    violations = []
    ra = fields.get("riskAppetite", "")
    sp = fields.get("strategicPriority", "")
    reg = fields.get("regulatoryEnvironment", "")
    size = fields.get("size", "")
    process = fields.get("innovationProcess", "")
    feedback = fields.get("customerFeedback", "")
    digital = fields.get("digitalMaturity", "")
    revenue = fields.get("revenueRange", "")
    budget = fields.get("budgetPercentage", -1)
    decision = fields.get("decisionMaking", "")
    barriers = fields.get("mainBarrier", [])
    comp = fields.get("competitivePressure", "")

    # 1. budgetPercentage ↔ riskAppetite
    if ra == "conservative" and isinstance(budget, (int, float)) and budget > 8:
        violations.append(f"budgetPercentage={budget}% too high for conservative risk appetite (expect 2-6%)")
    if ra == "balanced" and isinstance(budget, (int, float)) and budget > 18:
        violations.append(f"budgetPercentage={budget}% too high for balanced risk appetite (expect 5-15%)")
    if ra == "bold" and isinstance(budget, (int, float)) and budget < 8:
        violations.append(f"budgetPercentage={budget}% too low for bold risk appetite (expect 12-25%)")

    # 2. revenueRange ↔ size
    if size == "Micro" and revenue in ("10m_to_50m", "over_50m"):
        violations.append(f"Micro company with {revenue} revenue is unrealistic")
    if size == "Small" and revenue == "over_50m":
        violations.append(f"Small company with over_50m revenue is unrealistic")
    if size == "Large" and revenue in ("under_1m", "1m_to_10m"):
        violations.append(f"Large company with {revenue} revenue is unrealistic")

    # 3. decisionMaking ↔ size
    if size == "Micro" and decision not in ("owner_alone", "small_leadership_team"):
        violations.append(f"Micro company with {decision} governance is unrealistic")
    if size == "Small" and decision == "formal_committee":
        violations.append(f"Small company with formal_committee governance is unrealistic")
    if size == "Large" and decision in ("owner_alone",):
        violations.append(f"Large company with owner_alone governance is unrealistic")

    # 4. customerFeedback ↔ innovationProcess
    feedback_maturity = {"no_formal_process": 0, "informal_conversations": 1, "surveys_nps": 2, "dedicated_research": 3}
    process_maturity = {"none": 0, "informal": 1, "partial": 2, "formal": 3}
    fb_mat = feedback_maturity.get(feedback, -1)
    pr_mat = process_maturity.get(process, -1)
    if fb_mat >= 0 and pr_mat >= 0 and abs(fb_mat - pr_mat) > 1:
        violations.append(f"customerFeedback maturity ({feedback}) too far from innovationProcess ({process})")

    # 5. digitalMaturity ↔ innovationProcess + size
    try:
        dig_int = int(digital)
        pr_int = process_maturity.get(process, 0) + 1
        size_bonus = {"Micro": 0, "Small": 0, "Medium": 1, "Large": 1}.get(size, 0)
        expected_floor = max(1, pr_int - 2 + size_bonus)
        expected_ceil = min(4, pr_int + 2 + size_bonus)
        if dig_int < expected_floor:
            violations.append(f"digitalMaturity={digital} too low for {process} process + {size} size (expect {expected_floor}-{expected_ceil})")
        if dig_int > expected_ceil:
            violations.append(f"digitalMaturity={digital} too high for {process} process + {size} size (expect {expected_floor}-{expected_ceil})")
    except (ValueError, TypeError):
        pass

    # 6. High regulation → process barrier
    if reg == "high" and "process" not in barriers:
        violations.append(f"high regulatory environment should include 'process' in mainBarrier")

    # 7. Conservative risk → no radical expectations (informational, not blocking)
    if ra == "conservative" and process == "formal":
        pass  # conservative can have formal process, it's about the output not the input

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

def call_llm(combo_id: str, feedback: str, model: str, gpu_layers: int, num_predict: int) -> str:
    prompt = build_prompt(combo_id, feedback)
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={
            "num_predict": num_predict,
            "num_gpu": gpu_layers,
            "temperature": 0.8,  # diversity for different survey variants
        },
    )
    return response.message.content


# ──────────────────────────────────────────────────────────────────────
# Main one-shot generator
# ──────────────────────────────────────────────────────────────────────

def generate_one(index: int, model: str, gpu_layers: int, num_predict: int = 12288, max_retries: int = 5) -> str | None:
    survey = load_survey(index)
    ex_id = survey["id"]
    combo_id = survey["combo_id"]
    expected = {
        "riskAppetite": survey["fields"]["riskAppetite"],
        "strategicPriority": survey["fields"]["strategicPriority"],
        "regulatoryEnvironment": survey["fields"]["regulatoryEnvironment"],
    }

    out_path = OUTPUT_DIR / f"{ex_id}.json"
    if out_path.exists():
        print(f"  {ex_id} already exists, skipping")
        return None

    print(f"  [{index}] {ex_id}  {combo_id}")
    feedback = ""
    start = time.time()

    for attempt in range(1, max_retries + 1):
        raw_text = call_llm(combo_id, feedback, model, gpu_layers, num_predict)
        parsed = extract_json(raw_text)

        if not parsed or "company" not in parsed or "answers" not in parsed:
            feedback = "ERROR: Output was not valid JSON or missing 'company'/'answers' keys. Respond with ONLY the JSON object, no markdown, no backticks, no explanation."
            print(f"    Attempt {attempt}: unparseable JSON")
            continue

        company = parsed.get("company", {})
        answers = parsed.get("answers", {})
        llm_output = parsed.get("output", {})

        violations = validate_fields(answers)

        if not violations:
            c_violations = []
            try:
                validate_enum(company.get("sector"), SECTORS, "sector")
            except ValidationError as e:
                c_violations.append(str(e))
            try:
                validate_enum(company.get("size"), SIZES, "size")
            except ValidationError as e:
                c_violations.append(str(e))
            violations.extend(c_violations)

            if not violations:
                merged = {**answers, "sector": company.get("sector", ""), "size": company.get("size", "")}
                violations = validate_correlations(merged)

        if not violations:
            combo_ok = (
                answers.get("riskAppetite") == expected["riskAppetite"]
                and answers.get("strategicPriority") == expected["strategicPriority"]
                and answers.get("regulatoryEnvironment") == expected["regulatoryEnvironment"]
            )
            if not combo_ok:
                violations.append(
                    f"Output combo ({answers.get('riskAppetite')}|{answers.get('strategicPriority')}|"
                    f"{answers.get('regulatoryEnvironment')}) does not match expected ({combo_id})"
                )

        if violations:
            feedback = "VALIDATION ERRORS:\n" + "\n".join(f"  - {v}" for v in violations)
            print(f"    Attempt {attempt}: {len(violations)} violation(s)")
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
                "sector": company.get("sector", ""),
                "size": company.get("size", ""),
                "regulatory_environment": answers.get("regulatoryEnvironment", ""),
                "risk_appetite": answers.get("riskAppetite", ""),
                "strategic_priority": answers.get("strategicPriority", ""),
                "competitive_pressure": answers.get("competitivePressure", ""),
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
                    "name": company.get("companyName", ""),
                    "sector": company.get("sector", ""),
                    "size": company.get("size", ""),
                },
                "answers": answers,
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
    parser = argparse.ArgumentParser(description="One-shot survey JSON generation with validation.")
    parser.add_argument("index", type=int, help="Index into raw_inputs.json (0-based)")
    parser.add_argument("--model", default="gemma4:e2b-it-qat", help="Ollama model name")
    parser.add_argument("--gpu-layers", type=int, default=-1, help="GPU layers (-1=all, 0=CPU)")
    parser.add_argument("--num-predict", type=int, default=12288, help="Max output tokens")
    parser.add_argument("--retries", type=int, default=5, help="Max retry attempts on validation failure")
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
