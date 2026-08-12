import strawberry
import json
from typing import List, Optional
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from .models import Company, QuestionnaireResponse, InnovationInsight, LLMTrace
from .services.llm_services import generate_innovation_insight, _extract_json
from .services.memory import build_assessment_history, build_score_trend


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
    id: str = ""
    type: str = ""
    title: str = ""
    rationale: str = ""
    execution_plan: Optional[ExecutionPlanType] = None
    impact: str = ""
    difficulty: str = ""
    timeframe: str = ""
    carry_forward_from: Optional[str] = None
    carry_forward_status: Optional[str] = None


@strawberry.type
class NextStepType:
    id: str = ""
    action: str = ""
    owner: str = ""
    timeframe: str = ""


@strawberry.type
class ProgressReportType:
    improvements: List[str]
    persistent_gaps: List[str]
    achieved_milestones: List[str]


@strawberry.type
class ComparisonType:
    previous_score: Optional[float] = None
    previous_date: Optional[str] = None
    assessment_number: Optional[int] = None
    key_changes: Optional[str] = None


@strawberry.type
class InsightType:
    id: int
    ai_output: str
    innovation_score: Optional[float]
    score_delta: Optional[float] = None
    opportunities: List[OpportunityType]
    next_steps: List[NextStepType]
    key_weaknesses: List[str]
    progress: Optional[ProgressReportType] = None
    comparison_to_previous: Optional[ComparisonType] = None
    previous_insight_id: Optional[int] = None
    assessment_number: int = 1
    company_name: str = ""
    sector: str = ""
    size: str = ""
    previous_answers: str = ""


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
    innovation_score: Optional[float]
    submitted_at: str


@strawberry.type
class CompanySummaryType:
    id: int
    name: str
    sector: str
    size: str
    latest_score: Optional[float] = None
    latest_insight_id: Optional[int] = None
    assessment_count: int = 0
    created_at: str = ""


@strawberry.type
class AssessmentTimelineType:
    id: int
    assessment_number: int
    period_label: str
    innovation_score: Optional[float]
    score_delta: Optional[float]
    generated_at: str


@strawberry.type
class CompanyDetailType:
    id: int
    name: str
    sector: str
    size: str
    latest_score: Optional[float]
    score_trend: str
    delta: float
    assessment_count: int
    created_at: str
    assessments: List[AssessmentTimelineType]


# --- Helpers ---

def _insight_to_type(insight: InnovationInsight) -> InsightType:
    bundle = insight.context_bundle or {}

    opportunities = []
    for o in bundle.get("opportunities", []):
        exec_plan_data = o.get("execution_plan")
        exec_plan = ExecutionPlanType(**exec_plan_data) if exec_plan_data else None
        opportunities.append(
            OpportunityType(
                id=o.get("id", ""),
                type=o.get("type", ""),
                title=o.get("title", ""),
                rationale=o.get("rationale", ""),
                execution_plan=exec_plan,
                impact=o.get("impact", ""),
                difficulty=o.get("difficulty", ""),
                timeframe=o.get("timeframe", ""),
                carry_forward_from=o.get("carry_forward_from"),
                carry_forward_status=o.get("carry_forward_status"),
            )
        )

    next_steps = [
        NextStepType(
            id=s.get("id", ""),
            action=s.get("action", ""),
            owner=s.get("owner", ""),
            timeframe=s.get("timeframe", ""),
        )
        for s in bundle.get("next_steps", [])
    ]

    progress_data = bundle.get("progress")
    progress = (
        ProgressReportType(
            improvements=progress_data.get("improvements", []),
            persistent_gaps=progress_data.get("persistent_gaps", []),
            achieved_milestones=progress_data.get("achieved_milestones", []),
        )
        if progress_data
        else None
    )

    comp_data = bundle.get("comparison_to_previous")
    comparison = (
        ComparisonType(
            previous_score=comp_data.get("previous_score"),
            previous_date=comp_data.get("previous_date"),
            assessment_number=comp_data.get("assessment_number"),
            key_changes=comp_data.get("key_changes"),
        )
        if comp_data
        else None
    )

    previous_insight_id = insight.previous_insight_id
    assessment_number = insight.response.assessment_number
    company = insight.response.company
    previous_answers = json.dumps(insight.response.answers or {})

    return InsightType(
        id=insight.id,
        ai_output=insight.ai_output,
        innovation_score=insight.innovation_score,
        score_delta=insight.score_delta,
        opportunities=opportunities,
        next_steps=next_steps,
        key_weaknesses=bundle.get("key_weaknesses", []),
        progress=progress,
        comparison_to_previous=comparison,
        previous_insight_id=previous_insight_id,
        assessment_number=assessment_number,
        company_name=company.name,
        sector=company.sector,
        size=company.size,
        previous_answers=previous_answers,
    )


def _record_trace(insight, step_name, input_payload, output_payload,
                  duration_ms, model_name=""):
    LLMTrace.objects.create(
        insight=insight,
        step_name=step_name,
        model_name=model_name,
        input_payload=input_payload,
        output_payload=output_payload,
        duration_ms=duration_ms,
    )


def _get_or_create_company(info, company_id, company_name, sector, size):
    request = _get_request(info)
    if company_id is not None:
        try:
            company = Company.objects.get(id=company_id, user=request.user)
            company.name = company_name
            company.sector = sector
            company.size = size
            company.save()
            return company
        except Company.DoesNotExist:
            raise ValueError("Company not found")
    return Company.objects.create(
        name=company_name, sector=sector, size=size, user=request.user
    )


def _next_assessment_number(company):
    last = (
        QuestionnaireResponse.objects
        .filter(company=company)
        .order_by("-assessment_number")
        .values_list("assessment_number", flat=True)
        .first()
    )
    return (last or 0) + 1


def _create_response_and_insight(
    company,
    answers,
    previous_insight,
    assessment_number,
    period_label,
    changes_since_last,
    recommendation_status,
    request,
    model_name="",
) -> InsightType:
    """Core logic shared by submitQuestionnaire and submitReassessment."""
    effective_model = model_name or "gemma4"
    company_dict = {
        "name": company.name,
        "sector": company.sector,
        "size": company.size,
    }

    qr = QuestionnaireResponse.objects.create(
        company=company,
        assessment_number=assessment_number,
        period_label=period_label or "",
        changes_since_last=changes_since_last or "",
        recommendation_status=recommendation_status or {},
        answers=answers,
    )

    history = build_assessment_history(company, current_response=qr)

    from .services.llm_services import build_innovation_prompt
    actual_prompt = build_innovation_prompt(
        company_dict, answers, history if history else None
    )

    trace_rows = []

    def trace_cb(step_name, input_payload, output_payload, duration_ms):
        trace_rows.append({
            "step_name": step_name,
            "model_name": effective_model,
            "input_payload": input_payload,
            "output_payload": output_payload,
            "duration_ms": duration_ms,
        })

    ai_text, synth_duration_ms = generate_innovation_insight(
        company_dict, answers, history if history else None,
        model=effective_model, trace_cb=trace_cb
    )

    if not ai_text or not ai_text.strip():
        qr.delete()
        raise ValueError(
            "LLM returned empty response. The model may be unavailable "
            "or the prompt exceeded its context window."
        )

    parsed = _extract_json(ai_text)
    if not parsed:
        qr.delete()
        raise ValueError(
            "LLM response could not be parsed as JSON. "
            "Raw output (first 500 chars): " + str(ai_text)[:500]
        )

    score = parsed.get("maturity_score", None)
    score_delta = parsed.get("score_delta", None)

    insight = InnovationInsight.objects.create(
        response=qr,
        previous_insight=previous_insight,
        raw_prompt=actual_prompt,
        ai_output=ai_text,
        innovation_score=score,
        score_delta=score_delta,
        model_name=effective_model,
        context_bundle=parsed,
    )

    for tr in trace_rows:
        LLMTrace.objects.create(
            insight=insight,
            step_name=tr["step_name"],
            model_name=tr["model_name"],
            input_payload=tr["input_payload"],
            output_payload=tr["output_payload"],
            duration_ms=tr["duration_ms"],
        )

    return _insight_to_type(insight)


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

    @strawberry.field
    def my_companies(self, info: strawberry.types.Info) -> List[CompanySummaryType]:
        _guard(info)
        request = _get_request(info)
        companies = Company.objects.filter(user=request.user).order_by("-created_at")

        result = []
        for c in companies:
            trend = build_score_trend(c)
            last_insight = (
                InnovationInsight.objects
                .filter(response__company=c)
                .order_by("-generated_at")
                .values_list("id", flat=True)
                .first()
            )
            result.append(
                CompanySummaryType(
                    id=c.id,
                    name=c.name,
                    sector=c.sector,
                    size=c.size,
                    latest_score=trend["latest_score"],
                    latest_insight_id=last_insight,
                    assessment_count=trend["assessment_count"],
                    created_at=c.created_at.isoformat(),
                )
            )
        return result

    @strawberry.field
    def company(self, info: strawberry.types.Info, id: int) -> CompanyDetailType | None:
        _guard(info)
        request = _get_request(info)
        try:
            company = Company.objects.get(id=id, user=request.user)
        except Company.DoesNotExist:
            return None

        trend = build_score_trend(company)

        assessments = []
        insights = (
            InnovationInsight.objects
            .filter(response__company=company)
            .order_by("response__assessment_number")
            .select_related("response")
        )
        for i in insights:
            assessments.append(
                AssessmentTimelineType(
                    id=i.id,
                    assessment_number=i.response.assessment_number,
                    period_label=i.response.period_label or "",
                    innovation_score=i.innovation_score,
                    score_delta=i.score_delta,
                    generated_at=i.generated_at.isoformat(),
                )
            )

        return CompanyDetailType(
            id=company.id,
            name=company.name,
            sector=company.sector,
            size=company.size,
            latest_score=trend["latest_score"],
            score_trend=trend["trend"],
            delta=trend["delta"],
            assessment_count=trend["assessment_count"],
            created_at=company.created_at.isoformat(),
            assessments=assessments,
        )


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
        answers: strawberry.scalars.JSON,
        company_id: Optional[int] = None,
        period_label: Optional[str] = None,
    ) -> InsightType:
        _guard(info)
        request = _get_request(info)

        company = _get_or_create_company(
            info, company_id, company_name, sector, size
        )
        assessment_number = _next_assessment_number(company)

        return _create_response_and_insight(
            company=company,
            answers=answers,
            previous_insight=None,
            assessment_number=assessment_number,
            period_label=period_label or "",
            changes_since_last="",
            recommendation_status={},
            request=request,
        )

    @strawberry.mutation
    def submit_reassessment(
        self,
        info: strawberry.types.Info,
        company_id: int,
        company_name: str,
        sector: str,
        size: str,
        answers: strawberry.scalars.JSON,
        previous_insight_id: int,
        recommendation_status: Optional[strawberry.scalars.JSON] = None,
        changes_since_last: Optional[str] = None,
        period_label: Optional[str] = None,
    ) -> InsightType:
        _guard(info)
        request = _get_request(info)

        company = _get_or_create_company(
            info, company_id, company_name, sector, size
        )

        try:
            previous_insight = InnovationInsight.objects.get(
                id=previous_insight_id,
                response__company=company,
            )
        except InnovationInsight.DoesNotExist:
            raise ValueError("Previous insight not found for this company")

        assessment_number = _next_assessment_number(company)

        return _create_response_and_insight(
            company=company,
            answers=answers,
            previous_insight=previous_insight,
            assessment_number=assessment_number,
            period_label=period_label or "",
            changes_since_last=changes_since_last or "",
            recommendation_status=recommendation_status or {},
            request=request,
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
