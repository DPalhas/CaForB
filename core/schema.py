# core/schema.py
import strawberry
from .models import Company, QuestionnaireResponse, InnovationInsight
from .services.llm_services import generate_innovation_insight


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return "ok"


@strawberry.type
class InsightType:
    id: int
    ai_output: str
    innovation_score: float | None


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
        insight = InnovationInsight.objects.create(
            response=qr,
            raw_prompt=str(answers),
            ai_output=ai_text
        )
        return InsightType(id=insight.id, ai_output=ai_text, innovation_score=None)


schema = strawberry.Schema(query=Query, mutation=Mutation)
