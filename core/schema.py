import strawberry
import json
from typing import List
from .models import Company, QuestionnaireResponse, InnovationInsight, LLMTrace
from .services.llm_services import generate_innovation_insight


# --- Output Types ---

@strawberry.type
class OpportunityType:
    type: str
    title: str
    rationale: str
    impact: str
    difficulty: str
    timeframe: str


@strawberry.type
class InsightType:
    id: int
    ai_output: str
    innovation_score: float | None
    opportunities: List[OpportunityType]
    next_steps: List[str]
    key_weaknesses: List[str]


# --- Helper ---

def _insight_to_type(insight: InnovationInsight) -> InsightType:
    bundle = insight.context_bundle or {}
    opportunities = [
        OpportunityType(**o) for o in bundle.get("opportunities", [])
    ]
    return InsightType(
        id=insight.id,
        ai_output=insight.ai_output,
        innovation_score=insight.innovation_score,
        opportunities=opportunities,
        next_steps=bundle.get("next_steps", []),
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

        try:
            parsed = json.loads(ai_text)
            score = parsed.get("maturity_score", None)
        except (json.JSONDecodeError, AttributeError):
            parsed = {}
            score = None

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