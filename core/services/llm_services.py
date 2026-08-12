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

DEFAULT_MODEL = "gemma4"

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
- Strategic priority ({strategic_priority}) should shape the "title" and "rationale" of each opportunity so they visibly serve that priority: "growth" opportunities should target new revenue, customers or markets; "efficiency" opportunities should target cost reduction or process optimization; "market_defense" opportunities should target retention, competitive moats or countering specific competitor moves; "diversification" opportunities should target new products, verticals or business models distinct from the core business."""

_EXECUTION_CRITICAL = """Keep execution plans concise — use short phrases.
- "first_actions": 2-3 concrete immediate steps
- "resources_needed": 1-2 specific items (tools, budget, headcount)
- "success_metric": a KPI with a target number
- "milestones": 2 timed milestones
- Budget asks must stay within the estimated innovation budget.
- High-regulation environments require compliance steps in first_actions."""


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

IMPORTANT: Respond with a single valid JSON object only, in this format:
{_REASSESSMENT_JSON}

No markdown, no explanation, no extra text. Do NOT prefix positive numbers with a + sign.
Ensure all arrays are closed with ] and the object is closed with }}.
Keep rationale to 1 sentence. Provide 2-3 key_weaknesses.
Limit opportunities to 2 and next_steps to 2.
Do NOT write empty arrays — if there is no content, omit the field.
Ensure the complete JSON fits in your response — do not truncate."""


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
        options={"num_predict": 4096}
    )
    duration_ms = int((time.time() - start) * 1000)
    raw_text = response["message"]["content"]
    if trace_cb:
        trace_cb("llm_inference", {"model": model, "prompt_len": len(prompt)},
                 {"raw_text_len": len(raw_text)}, duration_ms)
    return raw_text, duration_ms


def generate_innovation_insight(company: dict, answers: dict,
                                history: Optional[str] = None,
                                model: str = DEFAULT_MODEL,
                                trace_cb: Optional[Callable] = None
                                ) -> tuple[str, int]:
    """
    Generate innovation insight for a company assessment.

    If history is provided, uses a two-phase approach:
      Phase 1 - score + opportunities
      Phase 2 - next steps + weaknesses + progress + comparison
    """
    is_reassessment = bool(history)

    if trace_cb:
        trace_cb("resolve_context",
                 {"is_reassessment": is_reassessment, "has_history": bool(history)},
                 {"assessment_type": "reassessment" if is_reassessment else "first"}, 0)

    if is_reassessment:
        return _generate_reassessment(company, answers, history, model, trace_cb)
    else:
        prompt = build_innovation_prompt(company, answers)
        if trace_cb:
            trace_cb("build_prompt", {"assessment_type": "first"},
                     {"prompt_len": len(prompt)}, 0)
        return _ollama_chat(model, prompt, trace_cb)


def _generate_reassessment(company, answers, history, model, trace_cb):
    """Two-phase LLM approach for reassessments."""
    total_duration = 0

    # Phase 1: Score + Opportunities
    p1 = _build_phase1_prompt(company, answers, history)
    if trace_cb:
        trace_cb("phase1_build_prompt", {"phase": 1},
                 {"prompt_len": len(p1)}, 0)
    t1, d1 = _ollama_chat(model, p1, trace_cb)
    total_duration += d1
    parsed1 = _extract_json(t1) or {}
    if trace_cb:
        trace_cb("phase1_parsed", {"phase": 1},
                 {"keys": list(parsed1.keys()) if parsed1 else []}, d1)

    # Phase 2: Next Steps + Weaknesses + Progress + Comparison
    opps = parsed1.get("opportunities", [])
    p2 = _build_phase2_prompt(company, answers, history, opps)
    if trace_cb:
        trace_cb("phase2_build_prompt", {"phase": 2},
                 {"prompt_len": len(p2)}, 0)
    t2, d2 = _ollama_chat(model, p2, trace_cb)
    total_duration += d2
    parsed2 = _extract_json(t2) or {}
    if trace_cb:
        trace_cb("phase2_parsed", {"phase": 2},
                 {"keys": list(parsed2.keys()) if parsed2 else []}, d2)

    combined = {
        "maturity_score": parsed1.get("maturity_score"),
        "score_delta": parsed1.get("score_delta"),
        "score_change": parsed1.get("score_change"),
        "opportunities": opps,
        "next_steps": parsed2.get("next_steps", []),
        "key_weaknesses": parsed2.get("key_weaknesses", []),
        "progress": parsed2.get("progress", {}),
        "comparison_to_previous": parsed2.get("comparison_to_previous", {}),
        "_debug_phase1_raw": t1[:1000] if t1 else "(empty)",
    }
    combined_text = json.dumps(combined)
    return combined_text, total_duration


def _build_phase1_prompt(company, answers, history):
    """Score + Opportunities only."""
    constraints = _CONSTRAINT_RULES.format(
        estimated_budget=_estimate_budget(answers),
        decision_making=answers.get("decisionMaking", "unknown"),
        customer_feedback=answers.get("customerFeedback", "unknown"),
        regulatory_level=answers.get("regulatoryEnvironment", "unknown"),
        competitive_pressure=answers.get("competitivePressure", "unknown"),
        risk_appetite=answers.get("riskAppetite", "unknown"),
        strategic_priority=answers.get("strategicPriority", "unknown"),
    )

    return f"""You are a strategic innovation advisor.

{history}

Company: {company['name']} | Sector: {company['sector']} | Size: {company['size']}
Description: {answers.get('companyDescription', 'Not provided')}

PHASE 1 — SCORE & OPPORTUNITIES

Compare with the prior assessments above. Determine the updated maturity score
(0-10), score delta, score change, and 1-2 prioritized opportunities with
carry_forward tracking. Include execution plans — keep them brief.

{constraints}

Respond ONLY with valid JSON:
{{"maturity_score": <float 0-10>, "score_delta": <float>, "score_change": "improved|stable|declined", "opportunities": [{{"id": "<str>", "type": "incremental|radical", "title": "<str>", "rationale": "<1 sentence>", "execution_plan": {{"first_actions": ["<str>"], "resources_needed": ["<str>"], "success_metric": "<str>", "milestones": ["<str>"]}}, "impact": "low|medium|high", "difficulty": "low|medium|high", "timeframe": "<str>", "carry_forward_from": null, "carry_forward_status": "continues|evolved_to|retired|new"}}]}}
No markdown. No + before numbers."""


def _build_phase2_prompt(company, answers, history, opportunities):
    """Next Steps + Weaknesses + Progress + Comparison."""
    formatted_answers = json.dumps(answers, indent=2)
    opp_brief = []
    for o in (opportunities or []):
        opp_brief.append(f"- [{o.get('id','?')}] {o.get('type','?')}: {o.get('title','?')}")
    opp_summary = "\n".join(opp_brief) or "(none)"

    return f"""You are a strategic innovation advisor.

{history}

Company: {company['name']} | Sector: {company['sector']} | Size: {company['size']}

The following opportunities were already identified:
{opp_summary}

PHASE 2 — NEXT STEPS, WEAKNESSES, PROGRESS & COMPARISON

Generate the remaining assessment fields based on the company context and
opportunities above.

Respond ONLY with valid JSON:
{{"next_steps": [{{"id": "...", "action": "...", "owner": "...", "timeframe": "..."}}], "key_weaknesses": ["..."], "progress": {{"improvements": ["..."], "persistent_gaps": ["..."], "achieved_milestones": ["..."]}}, "comparison_to_previous": {{"previous_score": <float>, "previous_date": "...", "assessment_number": <int>, "key_changes": "..."}}}}
No markdown."""
