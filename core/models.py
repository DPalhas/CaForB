from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="companies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.sector})"


class QuestionnaireResponse(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="responses")
    assessment_number = models.PositiveIntegerField(default=1)
    period_label = models.CharField(max_length=100, blank=True, default="")
    changes_since_last = models.TextField(blank=True, default="")
    recommendation_status = models.JSONField(default=dict)
    answers = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company", "assessment_number"]

    def __str__(self):
        return f"Assessment #{self.assessment_number} for {self.company.name} at {self.submitted_at}"


class InnovationInsight(models.Model):
    response = models.ForeignKey(QuestionnaireResponse, on_delete=models.CASCADE, related_name="insights")
    previous_insight = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="subsequent_insights"
    )
    raw_prompt = models.TextField()
    ai_output = models.TextField()
    innovation_score = models.FloatField(null=True, blank=True)
    score_delta = models.FloatField(null=True, blank=True)
    model_name = models.CharField(max_length=100, blank=True, default="")
    is_selected = models.BooleanField(default=False)
    context_bundle = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight #{self.id} (score: {self.innovation_score})"


class LLMTrace(models.Model):
    insight = models.ForeignKey(InnovationInsight, on_delete=models.CASCADE, related_name="traces")
    step_name = models.CharField(max_length=100, default="single_inference")
    model_name = models.CharField(max_length=100, blank=True, default="")
    input_payload = models.JSONField()
    output_payload = models.JSONField()
    duration_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trace [{self.step_name}] for Insight #{self.insight_id} ({self.duration_ms}ms)"


class ChatSession(models.Model):
    insight = models.ForeignKey(
        InnovationInsight, on_delete=models.CASCADE, related_name="chat_sessions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatSession #{self.id} for Insight #{self.insight_id}"


class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20)
    content = models.TextField()
    tagged_opportunity_id = models.CharField(max_length=50, blank=True, default="")
    tagged_next_step_id = models.CharField(max_length=50, blank=True, default="")
    tagged_weakness = models.TextField(blank=True, default="")
    model_name = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"ChatMessage [{self.role}] in session #{self.session_id}"