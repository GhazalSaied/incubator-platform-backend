from django.contrib import admin
from .models import EvaluationCriterion,Evaluation,EvaluationScore
# Register your models here.
admin.site.register(EvaluationCriterion)
admin.site.register(Evaluation)
admin.site.register(EvaluationScore)