from django.urls import path
from .views import (
    EvaluationCreateUpdateAPIView,
    EvaluationSubmitAPIView,
    
)

urlpatterns = [
    path("idea/<int:idea_id>/", EvaluationCreateUpdateAPIView.as_view()),
    path("idea/<int:idea_id>/submit/", EvaluationSubmitAPIView.as_view()),
    #path("idea/<int:idea_id>/history/", MyEvaluationsAPIView.as_view()),
]
