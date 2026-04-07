from django.contrib import admin
from .models import EvaluationCriterion,Evaluation,EvaluationScore,EvaluationInvitation, IncubationReview,EvaluationAssignment

admin.site.register(EvaluationCriterion)
admin.site.register(Evaluation)
admin.site.register(EvaluationScore)
admin.site.register(EvaluationInvitation)
admin.site.register(IncubationReview)
admin.site.register(EvaluationAssignment)