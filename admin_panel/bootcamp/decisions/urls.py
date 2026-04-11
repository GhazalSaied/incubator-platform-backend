from django.urls import path
from .views import BootcampIdeasListView, BootcampDecisionView,EndCampView

urlpatterns = [
    path("ideas/", BootcampIdeasListView.as_view(), name="bootcamp-ideas"),
    path("decide/", BootcampDecisionView.as_view(), name="bootcamp-decision"),
    path("end-camp/<int:season_id>/", EndCampView.as_view(), name="end-camp"),
]