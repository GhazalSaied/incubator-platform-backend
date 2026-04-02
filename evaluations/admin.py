from django.contrib import admin
from .models import EvaluationCriterion,Evaluation,EvaluationScore,IdeaEvaluator

admin.site.register(EvaluationCriterion)
admin.site.register(Evaluation)
admin.site.register(EvaluationScore)
admin.site.register(IdeaEvaluator)