from django.contrib import admin
from .models import Company, QuestionnaireResponse, InnovationInsight, LLMTrace


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "sector", "size", "user", "created_at")
    search_fields = ("name", "sector")
    list_filter = ("sector", "size")


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ("company", "assessment_number", "period_label",
                    "submitted_at")
    search_fields = ("company__name",)
    list_filter = ("assessment_number",)


@admin.register(InnovationInsight)
class InnovationInsightAdmin(admin.ModelAdmin):
    list_display = ("id", "response", "innovation_score", "score_delta",
                    "model_name", "generated_at")
    search_fields = ("response__company__name", "model_name")
    list_filter = ("model_name",)


@admin.register(LLMTrace)
class LLMTraceAdmin(admin.ModelAdmin):
    list_display = ("id", "insight", "step_name", "model_name",
                    "duration_ms", "created_at")
    search_fields = ("step_name", "model_name")
    list_filter = ("step_name", "model_name")
