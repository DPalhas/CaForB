import strawberry
import json
from typing import List, Optional
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Company, QuestionnaireResponse, InnovationInsight, LLMTrace
from .services.llm_services import generate_innovation_insight, _extract_json


def _get_request(info: strawberry.types.Info):
    ctx = info.context
    if ctx is None:
        return None
    return getattr(ctx, "request", None)


def _guard(info: strawberry.types.Info) -> None:
    request = _get_request(info)
    if request is None or not request.user.is_authenticated:
        raise PermissionError("Authentication required")


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


@strawberry.type
class UserType:
    id: int
    username: str
    email: str


@strawberry.type
class AssessmentSummaryType:
    id: int
    company_name: str
    sector: str
    innovation_score: float | None
    submitted_at: str


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
    def me(self, info: strawberry.types.Info) -> UserType | None:
        request = _get_request(info)
        if request is not None and request.user.is_authenticated:
            return UserType(
                id=request.user.id,
                username=request.user.username,
                email=request.user.email,
            )
        return None

    @strawberry.field
    def get_insight(self, info: strawberry.types.Info, id: int) -> InsightType | None:
        _guard(info)
        request = _get_request(info)
        try:
            insight = InnovationInsight.objects.get(id=id)
            if insight.response.company.user_id != request.user.id:
                raise PermissionError("Authentication required")
            return _insight_to_type(insight)
        except InnovationInsight.DoesNotExist:
            return None

    @strawberry.field
    def my_insights(self, info: strawberry.types.Info) -> List[AssessmentSummaryType]:
        _guard(info)
        request = _get_request(info)
        insights = InnovationInsight.objects.filter(
            response__company__user=request.user
        ).order_by("-generated_at")

        return [
            AssessmentSummaryType(
                id=i.id,
                company_name=i.response.company.name,
                sector=i.response.company.sector,
                innovation_score=i.innovation_score,
                submitted_at=i.generated_at.isoformat(),
            )
            for i in insights
        ]


# --- Mutation ---

@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(
        self,
        info: strawberry.types.Info,
        username: str,
        password: str,
    ) -> UserType:
        request = _get_request(info)
        if request is None:
            raise PermissionError("Authentication context unavailable")
        user = authenticate(request, username=username, password=password)
        if user is None:
            raise ValueError("Invalid username or password")
        login(request, user)
        return UserType(id=user.id, username=user.username, email=user.email)

    @strawberry.mutation
    def register(
        self,
        info: strawberry.types.Info,
        username: str,
        email: str,
        password: str,
    ) -> UserType:
        request = _get_request(info)
        if request is None:
            raise PermissionError("Authentication context unavailable")
        if not username or not email or not password:
            raise ValueError("Username, email, and password are required")
        if User.objects.filter(username=username).exists():
            raise ValueError("Username already taken")
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already registered")
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        login(request, user)
        return UserType(id=user.id, username=user.username, email=user.email)

    @strawberry.mutation
    def logout(self, info: strawberry.types.Info) -> bool:
        request = _get_request(info)
        if request is not None:
            logout(request)
        return True

    @strawberry.mutation
    def submit_questionnaire(
            self,
            info: strawberry.types.Info,
            company_name: str,
            sector: str,
            size: str,
            answers: strawberry.scalars.JSON
    ) -> InsightType:
        _guard(info)
        request = _get_request(info)
        company = Company.objects.create(
            name=company_name, sector=sector, size=size, user=request.user
        )
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