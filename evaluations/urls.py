from django.urls import path
from .views import (
    EvaluationCreateUpdateAPIView,
    EvaluationSubmitAPIView,
    MyEvaluationDetailAPIView
)

urlpatterns = [
    path("idea/<int:idea_id>/evaluate/", EvaluationCreateUpdateAPIView.as_view()),
    path("idea/<int:idea_id>/submit/", EvaluationSubmitAPIView.as_view()),
    path("idea/<int:idea_id>/my/", MyEvaluationDetailAPIView.as_view()),
]
