import ollama
import time
import json
import re


REVENUE_RANGE_LABELS = {
    "under_1m": "Under €1M",
    "1m_to_10m": "€1M–€10M",
    "10m_to_50m": "€10M–€50M",
    "over_50m": "€50M+",
}

REVENUE_RANGE_MIDPOINTS = {
    "under_1m": 500_000,
    "1m_to_10m": 5_500_000,
    "10m_to_50m": 30_000_000,
    "over_50m": 75_000_000,
}


def _estimate_budget(answers: dict) -> str:
    pct = answers.get("budgetPercentage")
    revenue_key = answers.get("revenueRange")
    if pct is None or not revenue_key:
        return "unknown"

    midpoint = REVENUE_RANGE_MIDPOINTS.get(revenue_key)
    if midpoint is None:
        return f"{pct}% of revenue"

    estimated_amount = midpoint * (pct / 100)
    return f"~€{estimated_amount:,.0f}/year ({pct}% of {REVENUE_RANGE_LABELS.get(revenue_key, revenue_key)} revenue)"


def build_innovation_prompt(company: dict, answers: dict) -> str:
    formatted_answers = json.dumps(answers, indent=2)
    estimated_budget = _estimate_budget(answers)

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
- Estimated annual innovation budget: {estimated_budget}. Decision-making structure ({answers.get('decisionMaking', 'unknown')}) should directly influence the "difficulty" and "timeframe" values, as well as the concreteness of "resources_needed" in execution_plan. When estimating resources_needed (e.g. tools, headcount, consulting spend), stay within the realistic bounds of the estimated budget above. Low budget or single-owner approval should bias toward lower-difficulty, faster-timeframe opportunities with minimal resource asks unless justified otherwise.
- Customer feedback process ({answers.get('customerFeedback', 'unknown')}) should influence whether opportunities lean toward validated, incremental improvements or exploratory, radical bets.

CRITICAL REQUIREMENTS FOR EXECUTION PLANS:
- "first_actions" must be concrete and immediately actionable — name specific tools, roles, or deliverables. Avoid vague phrases like "establish a process" or "conduct analysis" without specifying what the process/analysis actually involves.
- "success_metric" must include a specific number or measurable target, not a vague direction like "improve customer satisfaction."
- "milestones" must include rough time markers (e.g. "Week 1", "Month 2") so the plan reads as a real roadmap, not a wishlist.
- Every "next_steps" item must specify who is responsible and a realistic timeframe — not just what should happen.
- "resources_needed" costs and headcount asks must stay proportionate to the estimated budget provided above — do not suggest six-figure investments for a company with a sub-€10k budget.

IMPORTANT: Respond with a single valid JSON object only. No markdown, no explanation, no extra text. 
Ensure all arrays are closed with ] and the object is closed with }}."""


def _extract_json(text: str) -> dict:
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


def generate_innovation_insight(company: dict, answers: dict):
    prompt = build_innovation_prompt(company, answers)
    start = time.time()
    response = ollama.chat(
        model="gemma4",
        messages=[{"role": "user", "content": prompt}]
    )
    duration_ms = int((time.time() - start) * 1000)
    raw_text = response['message']['content']
    return raw_text, duration_ms