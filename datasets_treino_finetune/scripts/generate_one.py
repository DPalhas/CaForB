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
REASSESS_INPUT_PATH = BASE_DIR / "raw_inputs_reassessment.json"
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
# Reassessment generation
# ──────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_REASSESSMENT = """You are a data generator for fine-tuning a corporate innovation reassessment AI.

You will receive a prior assessment summary, a description of changes since that assessment,
progress on previous recommendations, and an updated corporate survey.
Your job: generate a complete REASSESSMENT analysis with delta tracking, carry-forward of
previous opportunities, progress report, and comparison to the prior assessment.

RULES:
- Generate 1-2 opportunities with carry_forward tracking
- 2-3 next_steps, 2-3 key_weaknesses
- Score delta must match maturity_score change vs previous_score
- Conservative risk = all incremental; Bold = at least one radical
- High regulation = compliance steps in first_actions
- RESPOND WITH ONLY THE RAW JSON. No markdown. No explanation. No backticks."""


_REASSESSMENT_OUTPUT_TEMPLATE = """{
  "maturity_score": <float 0-10>,
  "score_delta": <float>,
  "score_change": "improved|stable|declined",
  "opportunities": [
    {
      "id": "<unique id>",
      "type": "incremental|radical",
      "title": "<string>",
      "rationale": "<2-3 sentences>",
      "execution_plan": {
        "first_actions": ["<3-4 steps>"],
        "resources_needed": ["<2-3 resources>"],
        "success_metric": "<measurable KPI>",
        "milestones": ["<2-3 milestones>"]
      },
      "impact": "low|medium|high",
      "difficulty": "low|medium|high",
      "timeframe": "<string>",
      "carry_forward_from": "<previous opp id or null>",
      "carry_forward_status": "continues|evolved_to|retired|new"
    }
  ],
  "next_steps": [
    {
      "id": "<unique id>",
      "action": "<specific action>",
      "owner": "<role>",
      "timeframe": "<string>"
    }
  ],
  "key_weaknesses": ["<2-3 items>"],
  "progress": {
    "improvements": ["<string>"],
    "persistent_gaps": ["<string>"],
    "achieved_milestones": ["<string>"]
  },
  "comparison_to_previous": {
    "previous_score": <float>,
    "previous_date": "<YYYY-MM-DD or unknown>",
    "assessment_number": <int>,
    "key_changes": "<brief summary>"
  }
}"""


def load_reassessment_survey(index: int) -> dict:
    with open(REASSESS_INPUT_PATH, "r", encoding="utf-8") as f:
        all_reassess = json.load(f)
    if index < 0 or index >= len(all_reassess):
        raise IndexError(f"Index {index} out of range (0..{len(all_reassess)-1})")
    return all_reassess[index]


def _format_prior_summary(prev: dict) -> str:
    """Format the previous assessment data into a compact summary block."""
    pf = prev.get("fields", prev)
    lines = ["--- PRIOR ASSESSMENT ---"]
    lines.append(f"Company: {pf.get('companyName', '?')}")
    lines.append(f"Sector: {pf.get('sector', '?')} | Size: {pf.get('size', '?')}")
    lines.append(f"Risk: {pf.get('riskAppetite', '?')} | Priority: {pf.get('strategicPriority', '?')}")
    if pf.get("innovationProcess"):
        lines.append(f"Innovation maturity: {pf.get('innovationProcess')}")
    lines.append(f"Regulatory: {pf.get('regulatoryEnvironment', '?')} | Competition: {pf.get('competitivePressure', '?')}")
    lines.append(f"Digital maturity: {pf.get('digitalMaturity', '?')}")
    lines.append(f"Budget: {pf.get('budgetPercentage', '?')}% of {pf.get('revenueRange', '?')}")
    if pf.get("mainBarrier"):
        lines.append(f"Barriers: {', '.join(pf.get('mainBarrier', []))}")
    return "\n".join(lines)


def build_reassessment_prompt(data: dict, feedback: str = "") -> str:
    fields = data["fields"]
    prev = data.get("previous_assessment", {})

    base = (
        f"Generate a REASSESSMENT training example.\n\n"
        f"Combo: {data.get('combo_id', '?')}\n\n"
        f"{_format_prior_summary(prev)}\n\n"
        f"--- CHANGES SINCE LAST ASSESSMENT ---\n"
        f"{data.get('changes_since_last', 'N/A')}\n\n"
        f"--- PROGRESS ON RECOMMENDATIONS ---\n"
        f"{json.dumps(data.get('recommendation_status', {}), indent=2)}\n\n"
        f"--- UPDATED SURVEY ---\n"
    )

    for key, val in fields.items():
        base += f"  {key}: {json.dumps(val)}\n"

    base += (
        f"\nConsider the prior assessment context. Determine the updated maturity score, "
        f"score delta vs the prior score, and carry-forward status for each opportunity. "
        f"Produce progress, next_steps, weaknesses, and comparison_to_previous.\n"
    )

    base += f"\nOutput MUST match this JSON structure:\n{_REASSESSMENT_OUTPUT_TEMPLATE}\n"

    if feedback:
        base += f"\n\nPREVIOUS ATTEMPT FAILED:\n{feedback}\n\nFix ALL violations and regenerate."

    return base


def extract_reassessment_json(text: str) -> dict:
    """Extract JSON without requiring 'company' key (reassessment has different format)."""
    for attempt in [
        lambda t: json.loads(t),
        lambda t: json.loads(re.search(r'\{.*\}', t, re.DOTALL).group()) if re.search(r'\{.*\}', t, re.DOTALL) else {},
        lambda t: json.loads(re.sub(r'\}\s*$', ']}', t.rstrip())),
        lambda t: json.loads(re.sub(r'(\s*\]?\s*)\}$', '\n  ]\n}', t.rstrip())),
    ]:
        try:
            result = attempt(text)
            if result and "maturity_score" in result:
                return result
        except (json.JSONDecodeError, AttributeError):
            continue
    return {}


def generate_reassessment_one(
    index: int,
    model: str,
    gpu_layers: int,
    num_predict: int = 12288,
    max_retries: int = 5,
) -> str | None:
    survey = load_reassessment_survey(index)
    reassess_id = survey["reassess_id"]
    fields = survey["fields"]
    base_id = survey["base_id"]

    out_path = OUTPUT_DIR / f"{reassess_id}.json"
    if out_path.exists():
        print(f"  {reassess_id} already exists, skipping")
        return None

    print(f"  [{index}] {reassess_id} (base: {base_id})")

    feedback = ""
    start = time.time()

    for attempt in range(1, max_retries + 1):
        prompt = build_reassessment_prompt(survey, feedback)
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_REASSESSMENT},
                {"role": "user", "content": prompt},
            ],
            options={
                "num_predict": num_predict,
                "num_gpu": gpu_layers,
                "temperature": 0.8,
            },
        )
        raw_text = response.message.content
        parsed = extract_reassessment_json(raw_text)

        if not parsed or "maturity_score" not in parsed:
            feedback = (
                "ERROR: Output was not valid JSON or missing maturity_score. "
                "Respond with ONLY the JSON object, no markdown, no backticks."
            )
            print(f"    Attempt {attempt}: unparseable JSON")
            continue

        violations = _validate_reassessment(parsed)
        if violations:
            feedback = "VALIDATION ERRORS:\n" + "\n".join(f"  - {v}" for v in violations)
            feedback += "\n\nFix ALL violations and regenerate."
            print(f"    Attempt {attempt}: {len(violations)} validation error(s)")
            for v in violations[:3]:
                print(f"      - {v}")
            continue

        duration_ms = int((time.time() - start) * 1000)

        result = {
            "id": reassess_id,
            "version": 1,
            "assessment_type": "reassessment",
            "base_id": base_id,
            "split": "train",
            "metadata": {
                "sector": fields["sector"],
                "size": fields["size"],
                "regulatory_environment": fields["regulatoryEnvironment"],
                "risk_appetite": fields["riskAppetite"],
                "strategic_priority": fields["strategicPriority"],
                "competitive_pressure": fields["competitivePressure"],
                "assessment_type": "reassessment",
                "reviewed": False,
                "source": f"{model}_synthetic",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "duration_ms": duration_ms,
                "attempts": attempt,
            },
            "instruction": (
                "You are a strategic corporate innovation advisor conducting a "
                "reassessment. Analyse the prior assessment summary, changes since "
                "last assessment, and updated survey, then respond with a complete "
                "reassessment JSON including score_delta, carry_forward, progress, "
                "and comparison_to_previous."
            ),
            "input": {
                "company": {
                    "name": fields.get("companyName", ""),
                    "sector": fields["sector"],
                    "size": fields["size"],
                },
                "answers": {k: v for k, v in fields.items()
                           if k not in ("companyName", "sector", "size")},
                "previous_assessment": survey.get("previous_assessment", {}),
                "changes_since_last": survey.get("changes_since_last", ""),
                "recommendation_status": survey.get("recommendation_status", {}),
            },
            "output": parsed,
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"    OK ({duration_ms}ms, {attempt} attempt(s))")
        return reassess_id

    print(f"    FAILED after {max_retries} attempts")
    return None


def _validate_reassessment(output: dict) -> list[str]:
    violations = []
    if "maturity_score" not in output:
        violations.append("missing maturity_score")
    if "opportunities" not in output or not isinstance(output["opportunities"], list):
        violations.append("missing or invalid opportunities")
    if "next_steps" not in output:
        violations.append("missing next_steps")
    if "key_weaknesses" not in output:
        violations.append("missing key_weaknesses")
    if "progress" not in output:
        violations.append("missing progress")
    if "comparison_to_previous" not in output:
        violations.append("missing comparison_to_previous")

    ms = output.get("maturity_score")
    if ms is not None and (not isinstance(ms, (int, float)) or ms < 0 or ms > 10):
        violations.append(f"maturity_score out of range: {ms}")

    for opp in output.get("opportunities", []):
        cfs = opp.get("carry_forward_status")
        if cfs and cfs not in ("continues", "evolved_to", "retired", "new"):
            violations.append(f"invalid carry_forward_status: {cfs} in {opp.get('id', '?')}")
        if opp.get("carry_forward_status") == "new" and opp.get("carry_forward_from"):
            violations.append(f"new opportunity should not have carry_forward_from: {opp.get('id', '?')}")

    cp = output.get("comparison_to_previous", {})
    if cp and "previous_score" not in cp:
        violations.append("comparison_to_previous missing previous_score")

    return violations


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="One-shot training example generation.")
    parser.add_argument("index", type=int, help="Index into input JSON (0-based)")
    parser.add_argument("--model", default="gemma4:e2b-it-qat", help="Ollama model name")
    parser.add_argument("--gpu-layers", type=int, default=-1, help="GPU layers (-1=all, 0=CPU)")
    parser.add_argument("--num-predict", type=int, default=12288, help="Max output tokens")
    parser.add_argument("--retries", type=int, default=5, help="Max retry attempts")
    parser.add_argument("--reassessment", action="store_true", help="Generate reassessment example")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Model: {args.model}")
    print(f"Device: {'GPU' if args.gpu_layers != 0 else 'CPU'}")
    print(f"Max retries: {args.retries}")
    print(f"Mode: {'reassessment' if args.reassessment else 'first-assessment'}")

    if args.reassessment:
        result = generate_reassessment_one(
            args.index, args.model, args.gpu_layers, args.num_predict, args.retries
        )
    else:
        result = generate_one(
            args.index, args.model, args.gpu_layers, args.num_predict, args.retries
        )

    if result:
        print(f"\nGenerated: raw/{result}.json")
    else:
        print(f"\nFailed to generate valid JSON")
        sys.exit(1)


if __name__ == "__main__":
    main()
