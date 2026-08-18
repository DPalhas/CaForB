import ollama
import time
import json
import re
from typing import Optional, Callable

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

DEFAULT_MODEL = "gemma4:12B"

# --- Budget estimation (unchanged) ---

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


# --- Constraint rules (shared between first assessment and reassessment) ---

_CONSTRAINT_RULES = """Consider the following when forming your assessment:
- Estimated annual innovation budget: {estimated_budget}. Decision-making structure ({decision_making}) should directly influence the "difficulty" and "timeframe" values, as well as the concreteness of "resources_needed" in execution_plan. When estimating resources_needed (e.g. tools, headcount, consulting spend), stay within the realistic bounds of the estimated budget above. Low budget or single-owner approval should bias toward lower-difficulty, faster-timeframe opportunities with minimal resource asks unless justified otherwise.
- Customer feedback process ({customer_feedback}) should influence whether opportunities lean toward validated, incremental improvements or exploratory, radical bets.
- Regulatory environment ({regulatory_level}) should directly influence "difficulty" and "timeframe": high regulation should push toward higher difficulty, longer timeframes, and "first_actions" that explicitly include compliance, legal review, or certification steps where relevant. Low regulation allows faster, more experimental timeframes without added compliance overhead.
- Competitive pressure ({competitive_pressure}) should influence the balance between "incremental" and "radical" opportunity types: high urgency should bias toward including at least one radical, faster-moving opportunity even if higher risk, while low urgency justifies purely incremental, longer-horizon suggestions. Explicitly reflect this urgency in the "rationale" field when relevant.
- Risk appetite ({risk_appetite}) should be the primary driver of the "type" field for each opportunity: "conservative" should produce mostly or entirely "incremental" opportunities with cautious framing in the rationale; "bold" should include at least one clearly "radical" opportunity even if difficulty is high; "balanced" should mix both types roughly evenly. Do not contradict a conservative risk appetite with a majority-radical opportunity list, even if competitive pressure is high — in that case, favor faster-timeframe incremental moves instead.
- Strategic priority ({strategic_priority}) should shape the "title" and "rationale" of each opportunity so they visibly serve that priority: "growth" opportunities should target new revenue, customers or markets; "efficiency" opportunities should target cost reduction or process optimization; "market_defense" opportunities should target retention, competitive moats or countering specific competitor moves; "diversification" opportunities should target new products, verticals or business models distinct from the core business.
- Tailoring: every opportunity and next step must reference the company's ACTUAL sector, product, or market (from the Company description and Sector above) — never generic SaaS/tech playbook advice. Name the company's real product category, customer type, or competitive context."""

_EXECUTION_CRITICAL = """CRITICAL REQUIREMENTS FOR EXECUTION PLANS:
- "first_actions" must be concrete and immediately actionable — name specific tools, roles, or deliverables. Avoid vague phrases like "establish a process" or "conduct analysis" without specifying what the process/analysis actually involves.
- "success_metric" must include a measurable BASELINE AND TARGET with numbers (e.g. "increase customer retention from 92% to 96%"), never a bare "improve by 15%" without a baseline.
- "milestones" must include rough time markers (e.g. "Month 1", "Quarter 2") so the plan reads as a real roadmap, not a wishlist.
- Every "next_steps" item must specify who is responsible and a realistic timeframe — not just what should happen.
- "resources_needed" must state an explicit euro amount for EVERY resource — either a one-off figure or an annual figure (e.g. "€5,000 one-off", "€40,000/year for 1 part-time project manager"). These figures must be a plausible fraction of the estimated innovation budget above. NEVER write vague costs like "low-cost tool", "some consulting", or "10 hours of staff time" without a concrete € figure.
- Every opportunity MUST include ALL execution_plan fields: first_actions, resources_needed, success_metric, and milestones. Do not omit any field."""


# --- Output JSON schemas ---

_FIRST_ASSESSMENT_JSON = """{
  "maturity_score": <float 0-10>,
  "opportunities": [
    {
      "id": "<unique short identifier e.g. opp_1>",
      "type": "incremental or radical",
      "title": "<string>",
      "rationale": "<string>",
      "execution_plan": {
        "first_actions": ["<specific, concrete first steps>"],
        "resources_needed": ["<specific tools, budget range, headcount, skills>"],
        "success_metric": "<measurable KPI with target number>",
        "milestones": ["<concrete milestone with timing>"]
      },
      "impact": "low, medium or high",
      "difficulty": "low, medium or high",
      "timeframe": "<string>"
    }
  ],
  "next_steps": [
    {
      "id": "<unique short identifier e.g. step_1>",
      "action": "<specific action>",
      "owner": "<role>",
      "timeframe": "<e.g. Within 2 weeks>"
    }
  ],
  "key_weaknesses": ["<string>"]
}"""

_REASSESSMENT_JSON = """{
  "maturity_score": <float 0-10>,
  "score_delta": <float — difference from previous score, e.g. 0.5 or -0.3>,
  "score_change": "improved | stable | declined",
  "opportunities": [
    {
      "id": "<unique identifier e.g. opp_2_1>",
      "type": "incremental or radical",
      "title": "<string>",
      "rationale": "<string>",
      "execution_plan": {
        "first_actions": ["<specific, concrete first steps>"],
        "resources_needed": ["<specific tools, budget range, headcount, skills>"],
        "success_metric": "<measurable KPI with target number>",
        "milestones": ["<concrete milestone with timing>"]
      },
      "impact": "low, medium or high",
      "difficulty": "low, medium or high",
      "timeframe": "<string>",
      "carry_forward_from": "<previous opportunity id or null>",
      "carry_forward_status": "continues | evolved_to | retired | new"
    }
  ],
  "next_steps": [
    {
      "id": "<unique identifier e.g. step_2_1>",
      "action": "<specific action>",
      "owner": "<role>",
      "timeframe": "<e.g. Within 2 weeks>"
    }
  ],
  "key_weaknesses": ["<string>"],
  "progress": {
    "improvements": ["<what improved since last assessment>"],
    "persistent_gaps": ["<problems that still persist>"],
    "achieved_milestones": ["<specific milestones achieved>"]
  },
  "comparison_to_previous": {
    "previous_score": <float>,
    "previous_date": "<YYYY-MM-DD>",
    "assessment_number": <int>,
    "key_changes": "<brief summary of what drove the score change>"
  }
}"""


# --- Prompt builders ---

_FEWSHOT_EXAMPLE = """Here is ONE illustrative example of the level of concreteness, euro-anchoring, and sector-tailoring expected. DO NOT copy it — tailor every detail to the actual company above:

{
  "id": "opp_1",
  "type": "incremental",
  "title": "Automated inventory reordering for the top 50 SKUs",
  "rationale": "The company is a mid-size wholesale distributor with a lean operations team; automating reorder points on its fastest-moving SKUs cuts stockout losses and frees the two warehouse staff for higher-value work.",
  "execution_plan": {
    "first_actions": [
      "Extract 12 months of SKU-level sales history from the existing ERP (Sage 200)",
      "Define min/max reorder thresholds for the top 50 SKUs with the warehouse supervisor",
      "Enable the built-in reorder module in the current ERP rather than buying a new tool"
    ],
    "resources_needed": [
      "ERP reorder module licence: €3,000/year",
      "0.25 FTE operations analyst: €11,000/year",
      "ERP consultant configuration: €2,400 one-off"
    ],
    "success_metric": "Reduce stockout incidents from 14 per quarter to 4 per quarter within 6 months",
    "milestones": [
      "Month 1: SKU history extracted and thresholds defined",
      "Month 2: ERP reorder module configured and tested",
      "Month 4: Live on all 50 SKUs, first stockout report reviewed"
    ]
  },
  "impact": "high",
  "difficulty": "medium",
  "timeframe": "6 months"
}"""


def _build_first_assessment_prompt(company: dict, answers: dict) -> str:
    formatted_answers = json.dumps(answers, indent=2)
    estimated_budget = _estimate_budget(answers)
    regulatory_level = answers.get("regulatoryEnvironment", "unknown")
    competitive_pressure = answers.get("competitivePressure", "unknown")
    risk_appetite = answers.get("riskAppetite", "unknown")
    strategic_priority = answers.get("strategicPriority", "unknown")

    constraints = _CONSTRAINT_RULES.format(
        estimated_budget=estimated_budget,
        decision_making=answers.get("decisionMaking", "unknown"),
        customer_feedback=answers.get("customerFeedback", "unknown"),
        regulatory_level=regulatory_level,
        competitive_pressure=competitive_pressure,
        risk_appetite=risk_appetite,
        strategic_priority=strategic_priority,
    )

    return f"""You are a strategic innovation advisor. Analyse the following company
profile and questionnaire responses, then respond ONLY with valid JSON in this exact format:
{_FIRST_ASSESSMENT_JSON}

Company: {company['name']} | Sector: {company['sector']} | Size: {company['size']}
Company description: {answers.get('companyDescription', 'Not provided')}

Questionnaire answers:
{formatted_answers}

{constraints}

{_EXECUTION_CRITICAL}

{_FEWSHOT_EXAMPLE}

Provide 3 prioritized opportunities, 3 next steps, and 3 key_weaknesses.

IMPORTANT: Respond with a single valid JSON object only. No markdown, no explanation, no extra text.
Ensure all arrays are closed with ] and the object is closed with }}."""


def _build_reassessment_prompt(company: dict, answers: dict, history: str) -> str:
    formatted_answers = json.dumps(answers, indent=2)
    estimated_budget = _estimate_budget(answers)
    regulatory_level = answers.get("regulatoryEnvironment", "unknown")
    competitive_pressure = answers.get("competitivePressure", "unknown")
    risk_appetite = answers.get("riskAppetite", "unknown")
    strategic_priority = answers.get("strategicPriority", "unknown")

    constraints = _CONSTRAINT_RULES.format(
        estimated_budget=estimated_budget,
        decision_making=answers.get("decisionMaking", "unknown"),
        customer_feedback=answers.get("customerFeedback", "unknown"),
        regulatory_level=regulatory_level,
        competitive_pressure=competitive_pressure,
        risk_appetite=risk_appetite,
        strategic_priority=strategic_priority,
    )

    return f"""You are a strategic innovation advisor conducting a REASSESSMENT
for a company you have previously evaluated.

{history}

CURRENT ASSESSMENT:
Company: {company['name']} | Sector: {company['sector']} | Size: {company['size']}
Company description: {answers.get('companyDescription', 'Not provided')}

Questionnaire answers:
{formatted_answers}

---

REASSESSMENT DIRECTIVES:

You are re-evaluating a company you assessed before. The PRIOR ASSESSMENT SUMMARY
above shows what you found last time, and what progress was made.

Your task:
1. Compare the current state against prior scores and opportunities.
2. Determine which prior opportunities continue, have evolved (e.g. from pilot to
   production), or should be retired (were completed, abandoned, or superseded).
3. Identify new opportunities based on changes since last assessment.
4. Assess overall progress: what improved, what persistent gaps remain, and
   which milestones were achieved.
5. Produce a "comparison_to_previous" block with the score change and its drivers.

For each opportunity, you MUST set:
- "carry_forward_from": the "id" of the previous opportunity this builds on
  (or null if entirely new).
- "carry_forward_status":
  - "continues" — the same opportunity, still in progress, refreshed
  - "evolved_to" — built upon a previous opportunity but significantly
    changed scope or approach
  - "retired" — completed, abandoned, or no longer relevant
  - "new" — no prior equivalent

Include all prior opportunities that are still relevant in your updated list.
Retired opportunities appear in the list with carry_forward_status="retired"
so the client can track closure — you may add a brief note in the rationale
explaining why it was retired.

{constraints}

{_EXECUTION_CRITICAL}

{_FEWSHOT_EXAMPLE}

IMPORTANT: Respond with a single valid JSON object only, in this format:
{_REASSESSMENT_JSON}

No markdown, no explanation, no extra text. Do NOT prefix positive numbers with a + sign.
Ensure all arrays are closed with ] and the object is closed with }}.
Provide 3 prioritized opportunities, 3 next steps, and 3 key_weaknesses.
Do NOT write empty arrays — if there is no content, omit the field."""


def build_innovation_prompt(company: dict, answers: dict,
                            history: Optional[str] = None) -> str:
    if history:
        return _build_reassessment_prompt(company, answers, history)
    return _build_first_assessment_prompt(company, answers)


# --- JSON extraction (unchanged) ---

def _repair_truncated_json(text: str) -> str:
    """Close any unbalanced brackets and quotes in incomplete JSON."""
    stack = []
    in_string = False
    escape = False
    for ch in text:
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
        elif not in_string:
            if ch == '{':
                stack.append('}')
            elif ch == '[':
                stack.append(']')
            elif ch == '}':
                if stack and stack[-1] == '}':
                    stack.pop()
            elif ch == ']':
                if stack and stack[-1] == ']':
                    stack.pop()
    if in_string:
        in_s = False
        esc = False
        for i in range(len(text) - 1, -1, -1):
            ch = text[i]
            if esc:
                esc = False
                continue
            if ch == '\\' and in_s:
                esc = True
                continue
            if ch == '"':
                in_s = not in_s
            elif not in_s and ch in ',:{[':
                text = text[:i + 1]
                break

    if stack:
        text = re.sub(r'[,\s]+$', '', text)
        text += ''.join(reversed(stack))
    return text


def _extract_json(text: str) -> dict:
    text = re.sub(r':\s*\+(\d)', r': \1', text)
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
    try:
        repaired = _repair_truncated_json(text)
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass
    return {}


# --- Agent loop ---

def _ollama_chat(model: str, prompt: str,
                 trace_cb: Optional[Callable] = None) -> tuple[str, int]:
    start = time.time()
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        think=False,
        options={"num_predict": 16384, "temperature": 0.3, "num_ctx": 8192}
    )
    duration_ms = int((time.time() - start) * 1000)
    raw_text = response["message"]["content"]
    if trace_cb:
        trace_cb("llm_inference", {"model": model, "prompt_len": len(prompt)},
                 {"raw_text_len": len(raw_text)}, duration_ms)
    return raw_text, duration_ms


_RETRY_SUFFIX = (
    "\n\nRespond with a single valid JSON object only — no reasoning, no thinking, "
    "no markdown, no prose. Include a numeric \"maturity_score\". Ensure all arrays "
    "are closed with ] and the object is closed with }."
)


def _chat_with_retry(model: str, prompt: str, trace_cb: Optional[Callable],
                     max_attempts: int = 3) -> tuple[str, int, int]:
    """Call the LLM, retrying on empty/unparseable/no-score responses.

    Both the base model and the fine-tuned model pass through this same function,
    so the retry policy is symmetric for A/B benchmarking. Returns
    (raw_text, total_duration_ms, attempts).
    """
    total_duration = 0
    attempts = 0
    last_raw = ""

    for attempt in range(1, max_attempts + 1):
        attempts = attempt
        p = prompt if attempt == 1 else prompt + _RETRY_SUFFIX
        raw, dur = _ollama_chat(model, p, trace_cb)
        total_duration += dur
        last_raw = raw

        if not raw or not raw.strip():
            if trace_cb:
                trace_cb("retry_empty", {"attempt": attempt},
                         {"reason": "empty response"}, dur)
            continue

        parsed = _extract_json(raw)
        if not parsed:
            if trace_cb:
                trace_cb("retry_unparseable", {"attempt": attempt},
                         {"reason": "unparseable json", "raw_head": raw[:200]}, dur)
            continue

        if parsed.get("maturity_score") is None:
            if trace_cb:
                trace_cb("retry_no_score", {"attempt": attempt},
                         {"reason": "missing maturity_score"}, dur)
            continue

        return raw, total_duration, attempts

    return last_raw, total_duration, attempts


def generate_innovation_insight(company: dict, answers: dict,
                                history: Optional[str] = None,
                                model: str = DEFAULT_MODEL,
                                trace_cb: Optional[Callable] = None
                                ) -> tuple[str, int]:
    """
    Generate innovation insight for a company assessment.

    Single-call for both first assessments and reassessments:
    - First assessment (no history): standard contract
      (maturity_score, opportunities, next_steps, key_weaknesses).
    - Reassessment (history present): full extended contract in one call
      (maturity_score, score_delta, score_change, opportunities with carry_forward,
      next_steps, key_weaknesses, progress, comparison_to_previous).

    Retries (same policy for any model) on empty, unparseable, or missing-score
    responses, up to 3 attempts.
    """
    is_reassessment = bool(history)

    if trace_cb:
        trace_cb("resolve_context",
                 {"is_reassessment": is_reassessment, "has_history": bool(history)},
                 {"assessment_type": "reassessment" if is_reassessment else "first"}, 0)

    prompt = build_innovation_prompt(company, answers, history)
    if trace_cb:
        trace_cb("build_prompt",
                 {"assessment_type": "reassessment" if is_reassessment else "first",
                  "prompt_len": len(prompt)},
                 {"prompt_len": len(prompt)}, 0)

    raw_text, duration_ms, attempts = _chat_with_retry(model, prompt, trace_cb)
    if trace_cb:
        trace_cb("finalize", {"attempts": attempts, "duration_ms": duration_ms},
                 {"raw_text_len": len(raw_text) if raw_text else 0}, 0)

    return raw_text, duration_ms


