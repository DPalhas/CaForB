#!/usr/bin/env python3
"""
generate_synthetic.py — Phase 2 of the CaForB fine-tuning data pipeline.

Reads raw_inputs.json, sends each survey to a local Ollama LLM, extracts the
structured JSON output, and saves each result as a training example in raw/XXXX.json.

Resume-friendly: skips examples that already have output files.

Usage:
    python scripts/generate_synthetic.py
    python scripts/generate_synthetic.py --model gemma4 --start 0 --limit 10
    python scripts/generate_synthetic.py --model mistral --resume
"""

import json
import time
import re
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import ollama

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "raw_inputs.json"
OUTPUT_DIR = BASE_DIR / "raw"
INSTRUCTION = (
    "You are a strategic corporate innovation advisor. "
    "Analyse the company profile and survey responses, then respond ONLY with a valid "
    "JSON object. Apply all constraints consistently: budget limits, regulatory burden, "
    "risk appetite alignment, competitive urgency, and strategic priority focus. "
    "Do not include markdown, explanations, or text outside the JSON object."
)

REVENUE_RANGE_LABELS = {
    "under_1m": "Under 1M",
    "1m_to_10m": "1M-10M",
    "10m_to_50m": "10M-50M",
    "over_50m": "50M+",
}

REVENUE_RANGE_MIDPOINTS = {
    "under_1m": 500_000,
    "1m_to_10m": 5_500_000,
    "10m_to_50m": 30_000_000,
    "over_50m": 75_000_000,
}


# ──────────────────────────────────────────────────────────────────────
# Budget estimation (mirrors llm_services._estimate_budget)
# ──────────────────────────────────────────────────────────────────────

def estimate_budget(answers: dict) -> str:
    pct = answers.get("budgetPercentage")
    revenue_key = answers.get("revenueRange")
    if pct is None or not revenue_key:
        return "unknown"

    midpoint = REVENUE_RANGE_MIDPOINTS.get(revenue_key)
    if midpoint is None:
        return f"{pct}% of revenue"

    estimated = midpoint * (pct / 100)
    return (
        f"~{estimated:,.0f}/year "
        f"({pct}% of {REVENUE_RANGE_LABELS.get(revenue_key, revenue_key)} revenue)"
    )


# ──────────────────────────────────────────────────────────────────────
# Prompt builder (mirrors llm_services.build_innovation_prompt)
# ──────────────────────────────────────────────────────────────────────

def build_prompt(company: dict, answers: dict) -> str:
    formatted_answers = json.dumps(answers, indent=2)
    budget = estimate_budget(answers)
    regulatory = answers.get("regulatoryEnvironment", "unknown")
    comp_pressure = answers.get("competitivePressure", "unknown")
    risk_appetite = answers.get("riskAppetite", "unknown")
    strategic_priority = answers.get("strategicPriority", "unknown")

    return f"""You are a strategic innovation advisor. Analyse the following company 
profile and questionnaire responses, then respond ONLY with valid JSON in this exact format:
{{
  "maturity_score": <float 0-10>,
  "opportunities": [
    {{
      "type": "incremental or radical",
      "title": "<string>",
      "rationale": "<string>",
      "execution_plan": {{
        "first_actions": ["<specific, concrete first steps, e.g. named tools, roles, deliverables>"],
        "resources_needed": ["<specific tools, budget range, headcount, skills required>"],
        "success_metric": "<a single measurable KPI with a target number, e.g. 'Reduce quote turnaround from 5 days to 24 hours'>",
        "milestones": ["<concrete milestone with rough timing, e.g. 'Week 2: pilot with 3 clients'>"]
      }},
      "impact": "low, medium or high",
      "difficulty": "low, medium or high",
      "timeframe": "<string>"
    }}
  ],
  "next_steps": [
    {{
      "action": "<specific action, not vague>",
      "owner": "<who should own this, e.g. 'Operations lead' or 'Founder'>",
      "timeframe": "<e.g. 'Within 2 weeks'>"
    }}
  ],
  "key_weaknesses": ["<string>"]
}}

Company: {company['name']} | Sector: {company['sector']} | Size: {company['size']}
Company description: {answers.get('companyDescription', 'Not provided')}

Questionnaire answers:
{formatted_answers}

Consider the following when forming your assessment:
- Estimated annual innovation budget: {budget}. Decision-making structure ({answers.get('decisionMaking', 'unknown')}) should directly influence the "difficulty" and "timeframe" values, as well as the concreteness of "resources_needed" in execution_plan. When estimating resources_needed (e.g. tools, headcount, consulting spend), stay within the realistic bounds of the estimated budget above. Low budget or single-owner approval should bias toward lower-difficulty, faster-timeframe opportunities with minimal resource asks unless justified otherwise.
- Customer feedback process ({answers.get('customerFeedback', 'unknown')}) should influence whether opportunities lean toward validated, incremental improvements or exploratory, radical bets.
- Regulatory environment ({regulatory}) should directly influence "difficulty" and "timeframe": high regulation should push toward higher difficulty, longer timeframes, and "first_actions" that explicitly include compliance, legal review, or certification steps where relevant. Low regulation allows faster, more experimental timeframes without added compliance overhead.
- Competitive pressure ({comp_pressure}) should influence the balance between "incremental" and "radical" opportunity types: high urgency should bias toward including at least one radical, faster-moving opportunity even if higher risk, while low urgency justifies purely incremental, longer-horizon suggestions. Explicitly reflect this urgency in the "rationale" field when relevant.
- Risk appetite ({risk_appetite}) should be the primary driver of the "type" field for each opportunity: "conservative" should produce mostly or entirely "incremental" opportunities with cautious framing in the rationale; "bold" should include at least one clearly "radical" opportunity even if difficulty is high; "balanced" should mix both types roughly evenly. Do not contradict a conservative risk appetite with a majority-radical opportunity list, even if competitive pressure is high -- in that case, favor faster-timeframe incremental moves instead.
- Strategic priority ({strategic_priority}) should shape the "title" and "rationale" of each opportunity so they visibly serve that priority: "growth" opportunities should target new revenue, customers or markets; "efficiency" opportunities should target cost reduction or process optimization; "market_defense" opportunities should target retention, competitive moats or countering specific competitor moves; "diversification" opportunities should target new products, verticals or business models distinct from the core business.

CRITICAL REQUIREMENTS FOR EXECUTION PLANS:
- "first_actions" must be concrete and immediately actionable -- name specific tools, roles, or deliverables. Avoid vague phrases like "establish a process" or "conduct analysis" without specifying what the process/analysis actually involves.
- "success_metric" must include a specific number or measurable target, not a vague direction like "improve customer satisfaction."
- "milestones" must include rough time markers (e.g. "Week 1", "Month 2") so the plan reads as a real roadmap, not a wishlist.
- Every "next_steps" item must specify who is responsible and a realistic timeframe -- not just what should happen.
- "resources_needed" costs and headcount asks must stay proportionate to the estimated budget provided above -- do not suggest six-figure investments for a company with a sub-10k budget.

IMPORTANT: Respond with a single valid JSON object only. No markdown, no explanation, no extra text. 
Ensure all arrays are closed with ] and the object is closed with }}."""


# ──────────────────────────────────────────────────────────────────────
# JSON extraction (mirrors llm_services._extract_json)
# ──────────────────────────────────────────────────────────────────────

def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    try:
        fixed = re.sub(r'\}\s*$', ']}', text.rstrip())
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    try:
        fixed = text.rstrip()
        if not fixed.endswith(']}'):
            fixed = re.sub(r'(\s*\]?\s*)\}$', '\n  ]\n}', fixed)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    return {}


# ──────────────────────────────────────────────────────────────────────
# LLM caller — Python SDK with subprocess fallback for thinking models
# ──────────────────────────────────────────────────────────────────────

def _call_llm(model: str, prompt: str, gpu_layers: int, num_predict: int) -> str:
    """Call Ollama, falling back to subprocess if SDK returns empty (thinking models)."""

    # Try Python SDK first
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_predict": num_predict,
                "num_gpu": gpu_layers,
            },
        )
        raw = response.message.content
        if raw and len(raw.strip()) > 50:
            return raw
    except Exception:
        pass

    # Fallback: subprocess via `ollama run` (handles thinking model output)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(prompt)
        tmp_path = tmp.name

    try:
        gpu_flag = []
        if gpu_layers == 0:
            gpu_flag = ["--num-gpu", "0"]
        elif gpu_layers > 0:
            gpu_flag = ["--num-gpu", str(gpu_layers)]

        with open(tmp_path, "r", encoding="utf-8") as f:
            result = subprocess.run(
                ["ollama", "run", model]
                + gpu_flag
                + ["--nowordwrap", "--verbose"],
                stdin=f,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,
            )

        raw = result.stdout or ""

        # Strip ANSI escape codes
        raw = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw)
        raw = re.sub(r'\x1b\[\?25[hl]', '', raw)
        raw = re.sub(r'\x1b\[\?2026[hl]', '', raw)

        # Remove progress / loading characters
        raw = re.sub(r'[\u2800-\u28FF]', '', raw)  # braille spinner chars
        raw = re.sub(r'[⠙⠸⠴⠦⠧⠇⠏⠋⠹⠼]', '', raw)

        # Strip thinking block for qwen/reasoning models
        raw = re.sub(r'^.*?\.\.\.done thinking\.\s*', '', raw, flags=re.DOTALL)
        raw = re.sub(r'^[\s\S]*?Thinking\.\.\.[\s\S]*?\.\.\.done thinking\.\s*', '', raw)

        # Clean up extra whitespace
        raw = raw.strip()

        if raw and len(raw) > 50:
            return raw
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return ""


# ──────────────────────────────────────────────────────────────────────
# Single example generation
# ──────────────────────────────────────────────────────────────────────

def generate_one(ex: dict, model: str, gpu_layers: int = -1, num_predict: int = 8192, retries: int = 2) -> dict | None:
    fields = ex["fields"]
    company = {
        "name": fields["companyName"],
        "sector": fields["sector"],
        "size": fields["size"],
    }
    answers = {
        "companyDescription": fields["companyDescription"],
        "innovationProcess": fields["innovationProcess"],
        "pastInitiatives": fields["pastInitiatives"],
        "customerFeedback": fields["customerFeedback"],
        "strategicGoals": fields["strategicGoals"],
        "strategicPriority": fields["strategicPriority"],
        "timeHorizon": fields["timeHorizon"],
        "riskAppetite": fields["riskAppetite"],
        "teamSize": fields["teamSize"],
        "digitalMaturity": fields["digitalMaturity"],
        "revenueRange": fields["revenueRange"],
        "budgetPercentage": fields["budgetPercentage"],
        "decisionMaking": fields["decisionMaking"],
        "regulatoryEnvironment": fields["regulatoryEnvironment"],
        "competitivePressure": fields["competitivePressure"],
        "mainBarrier": fields["mainBarrier"],
        "additionalContext": fields["additionalContext"],
    }

    prompt = build_prompt(company, answers)

    for attempt in range(1, retries + 1):
        try:
            start = time.time()
            raw_text = _call_llm(model, prompt, gpu_layers, num_predict)
            duration_ms = int((time.time() - start) * 1000)
            parsed = extract_json(raw_text)

            if not parsed or "maturity_score" not in parsed:
                if attempt == retries:
                    fail_dir = BASE_DIR / "debug"
                    fail_dir.mkdir(exist_ok=True)
                    fail_path = fail_dir / f"{ex['id']}_raw_response.txt"
                    with open(fail_path, "w", encoding="utf-8") as ff:
                        ff.write(raw_text)
                    print(f"\n    Raw response saved to {fail_path}")
                    print(f"    Response length: {len(raw_text)} chars, "
                          f"Parsed: {list(parsed.keys()) if parsed else '(empty)'}")
                if attempt < retries:
                    continue
                return None

            output = {
                "id": ex["id"],
                "version": 1,
                "split": "train",
                "metadata": {
                    "sector": fields["sector"],
                    "size": fields["size"],
                    "regulatory_environment": fields["regulatoryEnvironment"],
                    "risk_appetite": fields["riskAppetite"],
                    "strategic_priority": fields["strategicPriority"],
                    "competitive_pressure": fields["competitivePressure"],
                    "estimated_budget_eur": _compute_budget_eur(fields),
                    "reviewed": False,
                    "source": f"{model}_synthetic",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "duration_ms": duration_ms,
                    "attempts": attempt,
                },
                "instruction": INSTRUCTION,
                "input": {
                    "company": company,
                    "answers": answers,
                },
                "output": parsed,
            }
            return output

        except Exception as err:
            print(f"  Attempt {attempt} failed: {err}")
            time.sleep(2)

    return None


def _compute_budget_eur(fields: dict) -> int | None:
    pct = fields.get("budgetPercentage")
    revenue_key = fields.get("revenueRange")
    if pct is None or not revenue_key:
        return None
    midpoint = REVENUE_RANGE_MIDPOINTS.get(revenue_key)
    if midpoint is None:
        return None
    return int(midpoint * (pct / 100))


# ──────────────────────────────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic LLM outputs for survey inputs.")
    parser.add_argument("--model", default="gemma4", help="Ollama model name (default: gemma4)")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    parser.add_argument("--limit", type=int, default=0, help="Max examples to process (0 = all)")
    parser.add_argument("--resume", action="store_true", help="Skip examples with existing output files")
    parser.add_argument("--retries", type=int, default=2, help="Retries on parse failure (default: 2)")
    parser.add_argument("--gpu-layers", type=int, default=-1, help="Layers to offload to GPU (-1 = all, 0 = CPU only, default: -1)")
    parser.add_argument("--num-predict", type=int, default=8192, help="Max output tokens (increase for thinking models, default: 8192)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        all_examples = json.load(f)

    end = args.start + args.limit if args.limit > 0 else len(all_examples)
    batch = all_examples[args.start : min(end, len(all_examples))]
    total = len(batch)

    gpu_mode = f"GPU ({args.gpu_layers} layers)" if args.gpu_layers != 0 else "CPU only"
    print(f"Model: {args.model}")
    print(f"Device: {gpu_mode}")
    print(f"Max tokens: {args.num_predict}")
    print(f"Input: {INPUT_PATH} ({len(all_examples)} total)")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Processing: {total} examples (indices {args.start}..{min(end, len(all_examples)) - 1})")
    if args.resume:
        print("Resume mode: skipping existing files")
    print()

    success_count = 0
    skip_count = 0
    fail_count = 0
    total_duration_ms = 0

    t_start = time.time()

    for i, ex in enumerate(batch):
        ex_id = ex["id"]
        out_path = OUTPUT_DIR / f"{ex_id}.json"

        if args.resume and out_path.exists():
            skip_count += 1
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"  [{i+1}/{total}] {ex_id}  SKIP (already exists)  "
                  f"| {rate:.1f} ex/min")
            continue

        combo = ex["combo_id"]
        print(f"  [{i+1}/{total}] {ex_id}  {combo}  ... ", end="", flush=True)

        result = generate_one(ex, args.model, args.gpu_layers, args.num_predict, args.retries)

        if result:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            success_count += 1
            dur = result["metadata"]["duration_ms"]
            total_duration_ms += dur
            print(f"OK  ({dur}ms)")
        else:
            fail_count += 1
            print("FAIL (could not parse JSON)")

        if (i + 1) % 5 == 0:
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed * 60 if elapsed > 0 else 0
            print(f"  --- Progress: {i+1}/{total}  "
                  f"OK: {success_count}  SKIP: {skip_count}  FAIL: {fail_count}  "
                  f"| {rate:.1f} ex/min")

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"  Complete: {success_count} generated, {skip_count} skipped, {fail_count} failed")
    print(f"  Total time: {elapsed:.0f}s  "
          f"Avg: {total_duration_ms // max(success_count, 1)}ms/example")
    print(f"  Rate: {success_count / elapsed * 60:.1f} valid examples/min")


if __name__ == "__main__":
    main()
