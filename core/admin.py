from django.contrib import admin
from .models import Company, QuestionnaireResponse, InnovationInsight, LLMTrace

admin.site.register(Company)
admin.site.register(QuestionnaireResponse)
admin.site.register(InnovationInsight)
admin.site.register(LLMTrace)
