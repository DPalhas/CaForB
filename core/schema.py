import strawberry
import json
from typing import List, Optional
from .models import Company, QuestionnaireResponse, InnovationInsight, LLMTrace
from .services.llm_services import generate_innovation_insight, _extract_json


# --- Output Types ---

@strawberry.type
class ExecutionPlanType:
    first_actions: List[str]
    resources_needed: List[str]
    success_metric: str
    milestones: List[str]


@strawberry.type
class OpportunityType:
    type: str
    title: str
    rationale: str
    execution_plan: Optional[ExecutionPlanType]
    impact: str
    difficulty: str
    timeframe: str


@strawberry.type
class NextStepType:
    action: str
    owner: str
    timeframe: str


@strawberry.type
class InsightType:
    id: int
    ai_output: str
    innovation_score: float | None
    opportunities: List[OpportunityType]
    next_steps: List[NextStepType]
    key_weaknesses: List[str]


# --- Helper ---

def _insight_to_type(insight: InnovationInsight) -> InsightType:
    bundle = insight.context_bundle or {}

    opportunities = []
    for o in bundle.get("opportunities", []):
        exec_plan_data = o.get("execution_plan")
        exec_plan = ExecutionPlanType(**exec_plan_data) if exec_plan_data else None

        opportunities.append(
            OpportunityType(
                type=o.get("type", ""),
                title=o.get("title", ""),
                rationale=o.get("rationale", ""),
                execution_plan=exec_plan,
                impact=o.get("impact", ""),
                difficulty=o.get("difficulty", ""),
                timeframe=o.get("timeframe", ""),
            )
        )

    next_steps = [
        NextStepType(
            action=s.get("action", ""),
            owner=s.get("owner", ""),
            timeframe=s.get("timeframe", ""),
        )
        for s in bundle.get("next_steps", [])
    ]

    return InsightType(
        id=insight.id,
        ai_output=insight.ai_output,
        innovation_score=insight.innovation_score,
        opportunities=opportunities,
        next_steps=next_steps,
        key_weaknesses=bundle.get("key_weaknesses", [])
    )


# --- Query ---

@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return "ok"

    @strawberry.field
    def get_insight(self, id: int) -> InsightType | None:
        try:
            insight = InnovationInsight.objects.get(id=id)
            return _insight_to_type(insight)
        except InnovationInsight.DoesNotExist:
            return None


# --- Mutation ---

@strawberry.type
class Mutation:
    @strawberry.mutation
    def submit_questionnaire(
            self,
            company_name: str,
            sector: str,
            size: str,
            answers: strawberry.scalars.JSON
    ) -> InsightType:
        company = Company.objects.create(name=company_name, sector=sector, size=size)
        qr = QuestionnaireResponse.objects.create(company=company, answers=answers)

        ai_text, duration_ms = generate_innovation_insight(
            {"name": company_name, "sector": sector, "size": size}, answers
        )

        parsed = _extract_json(ai_text)
        score = parsed.get("maturity_score", None)

        insight = InnovationInsight.objects.create(
            response=qr,
            raw_prompt=str(answers),
            ai_output=ai_text,
            innovation_score=score,
            context_bundle=parsed
        )

        LLMTrace.objects.create(
            insight=insight,
            step_name="single_inference",
            input_payload={
                "company": company_name,
                "sector": sector,
                "size": size,
                "answers": answers
            },
            output_payload=parsed,
            duration_ms=duration_ms
        )

        return _insight_to_type(insight)


schema = strawberry.Schema(query=Query, mutation=Mutation)