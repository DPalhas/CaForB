import json
from typing import Optional

from ..models import Company, InnovationInsight


MAX_PRIOR_ASSESSMENTS = 5


def build_score_trend(company: Company) -> dict:
    insights = (
        InnovationInsight.objects
        .filter(response__company=company, is_selected=True)
        .order_by("generated_at")
        .select_related("response")
    )
    scores = [
        {
            "assessment_number": i.response.assessment_number,
            "score": i.innovation_score,
            "date": i.generated_at.isoformat(),
            "insight_id": i.id,
        }
        for i in insights
        if i.innovation_score is not None
    ]
    if not scores:
        return {"scores": [], "trend": "stable", "first_score": None,
                "latest_score": None, "delta": 0, "assessment_count": 0}

    first = scores[0]["score"]
    last = scores[-1]["score"]
    delta = round(last - first, 2) if first is not None else 0

    if delta > 0.5:
        trend = "improving"
    elif delta < -0.5:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "scores": scores,
        "trend": trend,
        "first_score": first,
        "latest_score": last,
        "delta": delta,
        "assessment_count": len(scores),
    }


def _format_budget_history(company: Company) -> str:
    responses = list(
        company.responses
        .order_by("assessment_number")[:MAX_PRIOR_ASSESSMENTS]
    )
    lines = []
    for r in responses:
        answers = r.answers or {}
        pct = answers.get("budgetPercentage")
        revenue = answers.get("revenueRange")
        if pct is not None and revenue:
            midpoints = {
                "under_1m": 500_000,
                "1m_to_10m": 5_500_000,
                "10m_to_50m": 30_000_000,
                "over_50m": 75_000_000,
            }
            mp = midpoints.get(revenue, 0)
            budget = mp * (pct / 100)
            lines.append(
                f"- Assessment #{r.assessment_number}: "
                f"~€{budget:,.0f}/year ({pct}% of {revenue} revenue)"
            )
        else:
            lines.append(
                f"- Assessment #{r.assessment_number}: budget unknown"
            )
    return "\n".join(lines)


def _format_opportunities_summary(previous_insight: Optional[InnovationInsight],
                                  recommendation_status: Optional[dict]) -> str:
    if previous_insight is None:
        return ""
    bundle = previous_insight.context_bundle or {}
    opportunities = bundle.get("opportunities", [])
    if not opportunities:
        return ""

    lines = []
    for i, opp in enumerate(opportunities, 1):
        opp_id = opp.get("id", f"opp_{i}")
        status = (recommendation_status or {}).get(opp_id, "unknown")
        lines.append(
            f'{i}. [{opp.get("type", "?")}] "{opp.get("title", "")}" '
            f'(Impact: {opp.get("impact", "?")}, '
            f'Difficulty: {opp.get("difficulty", "?")}, '
            f'Timeframe: {opp.get("timeframe", "?")})'
        )
        if "execution_plan" in opp:
            ep = opp["execution_plan"]
            metric = ep.get("success_metric", "")
            if metric:
                lines.append(f'   KPI: {metric}')
        lines.append(f"   Status: {status.upper()}")
    return "\n".join(lines)


def _format_next_steps_summary(previous_insight: Optional[InnovationInsight],
                               recommendation_status: Optional[dict]) -> str:
    if previous_insight is None:
        return ""
    bundle = previous_insight.context_bundle or {}
    next_steps = bundle.get("next_steps", [])
    if not next_steps:
        return ""

    lines = []
    for i, step in enumerate(next_steps, 1):
        step_id = step.get("id", f"step_{i}")
        status = (recommendation_status or {}).get(step_id, "unknown")
        lines.append(
            f'{i}. "{step.get("action", "")}" → '
            f'Owner: {step.get("owner", "?")}, '
            f'Timeframe: {step.get("timeframe", "?")} → {status.upper()}'
        )
    return "\n".join(lines)


def build_assessment_history(company: Company,
                             current_response=None) -> str:
    prior_responses = list(
        company.responses
        .exclude(pk=current_response.pk if current_response else None)
        .order_by("assessment_number")
        .prefetch_related("insights")[:MAX_PRIOR_ASSESSMENTS]
    )
    if not prior_responses:
        return ""

    parts = ["---",
             "PRIOR ASSESSMENT SUMMARY",
             "---"]

    for i, qr in enumerate(prior_responses):
        insight = next(
            (ins for ins in qr.insights.all() if ins.is_selected),
            None,
        )
        if insight is None:
            continue

        parts.append(
            f"\nAssessment #{qr.assessment_number} "
            f"(dated {qr.submitted_at.strftime('%Y-%m-%d')})"
        )
        parts.append(
            f"Previous Maturity Score: {insight.innovation_score}"
        )

        bundle = insight.context_bundle or {}
        opportunities = bundle.get("opportunities", [])
        if opportunities:
            parts.append("\nPreviously Identified Opportunities:")
            rec_status = qr.recommendation_status or {}
            for j, opp in enumerate(opportunities, 1):
                opp_id = opp.get("id", f"opp_{j}")
                status = rec_status.get(opp_id, "not tracked")
                parts.append(
                    f'{j}. [{opp.get("type", "?")}] '
                    f'"{opp.get("title", "")}" '
                    f'(Impact: {opp.get("impact", "?")}, '
                    f'Difficulty: {opp.get("difficulty", "?")}, '
                    f'Timeframe: {opp.get("timeframe", "?")})'
                )
                ep = opp.get("execution_plan")
                if ep and ep.get("success_metric"):
                    parts.append(f'   KPI: {ep["success_metric"]}')
                parts.append(f'   Status: {status.upper()}')

        next_steps = bundle.get("next_steps", [])
        if next_steps:
            parts.append("\nPrevious Next Steps:")
            for k, step in enumerate(next_steps, 1):
                step_id = step.get("id", f"step_{k}")
                status = (qr.recommendation_status or {}).get(
                    step_id, "not tracked"
                )
                parts.append(
                    f'{k}. "{step.get("action", "")}" → '
                    f'Owner: {step.get("owner", "?")}, '
                    f'Timeframe: {step.get("timeframe", "?")} → '
                    f'{status.upper()}'
                )

        weaknesses = bundle.get("key_weaknesses", [])
        if weaknesses:
            parts.append("\nPrevious Key Weaknesses:")
            for w in weaknesses:
                parts.append(f"- {w}")

    parts.append("\n---")
    parts.append("BUDGET HISTORY:")
    parts.append(_format_budget_history(company))
    parts.append("---")

    if current_response and current_response.changes_since_last:
        parts.append(
            f"\nCHANGES SINCE LAST ASSESSMENT:\n"
            f"{current_response.changes_since_last}"
        )

    if current_response and current_response.recommendation_status:
        rec_status = current_response.recommendation_status
        parts.append("\nPROGRESS ON PREVIOUS RECOMMENDATIONS:")
        for key, value in rec_status.items():
            parts.append(f"- {key}: {value.upper()}")

    return "\n".join(parts)


def build_compact_history(company: Company,
                          current_response=None) -> str:
    """Shorter variant for use when token budget is tight."""
    prior_responses = list(
        company.responses
        .exclude(pk=current_response.pk if current_response else None)
        .order_by("-assessment_number")[:3]
        .prefetch_related("insights")
    )
    if not prior_responses:
        return ""

    lines = ["Previous assessments:"]
    for qr in reversed(prior_responses):
        insight = next(
            (ins for ins in qr.insights.all() if ins.is_selected),
            None,
        )
        score = insight.innovation_score if insight else "N/A"
        bundle = insight.context_bundle if insight else {}
        opp_count = len(bundle.get("opportunities", []))
        lines.append(
            f"  #{qr.assessment_number} ({qr.submitted_at.strftime('%Y-%m-%d')}): "
            f"score={score}, {opp_count} opportunities"
        )
    return "\n".join(lines)
