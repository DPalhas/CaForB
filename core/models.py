# core/models.py
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100)
    size = models.CharField(max_length=50)  # SME, Mid, Large
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.sector})"


class QuestionnaireResponse(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="responses")
    answers = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for {self.company.name} at {self.submitted_at}"


class InnovationInsight(models.Model):
    response = models.OneToOneField(QuestionnaireResponse, on_delete=models.CASCADE, related_name="insight")
    raw_prompt = models.TextField()
    ai_output = models.TextField()
    innovation_score = models.FloatField(null=True, blank=True)
    context_bundle = models.JSONField(default=dict)   # ← added
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight #{self.id} (score: {self.innovation_score})"


class LLMTrace(models.Model):                         # ← added
    insight = models.ForeignKey(InnovationInsight, on_delete=models.CASCADE, related_name="traces")
    step_name = models.CharField(max_length=100, default="single_inference")
    input_payload = models.JSONField()
    output_payload = models.JSONField()
    duration_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trace [{self.step_name}] for Insight #{self.insight_id} ({self.duration_ms}ms)"