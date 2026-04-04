from django.urls import path
from .views import BootcampIdeasListView, BootcampDecisionView

urlpatterns = [
    path("ideas/", BootcampIdeasListView.as_view(), name="bootcamp-ideas"),
    path("decide/", BootcampDecisionView.as_view(), name="bootcamp-decision"),
]