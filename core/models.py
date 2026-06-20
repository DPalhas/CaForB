from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100)
    size = models.CharField(max_length=50)  # SME, Mid, Large
    created_at = models.DateTimeField(auto_now_add=True)

class QuestionnaireResponse(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    answers = models.JSONField()  # Stores all Q&A pairs
    submitted_at = models.DateTimeField(auto_now_add=True)

class InnovationInsight(models.Model):
    response = models.OneToOneField(QuestionnaireResponse, on_delete=models.CASCADE)
    raw_prompt = models.TextField()
    ai_output = models.TextField()       # Gemma4's recommendation
    innovation_score = models.FloatField(null=True)
    generated_at = models.DateTimeField(auto_now_add=True)