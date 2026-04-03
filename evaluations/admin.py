from django.contrib import admin
from .models import EvaluationCriterion,Evaluation,EvaluationScore,IdeaEvaluator,EvaluationTemplate,EvaluationTemplateCriterion

admin.site.register(EvaluationCriterion)
admin.site.register(Evaluation)
admin.site.register(EvaluationScore)
admin.site.register(IdeaEvaluator)
admin.site.register(EvaluationTemplate)
admin.site.register(EvaluationTemplateCriterion)