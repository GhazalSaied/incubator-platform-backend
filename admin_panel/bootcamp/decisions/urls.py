from django.urls import path
from .views import BootcampIdeasListView, BootcampDecisionView, EndBootcampSessionsView

urlpatterns = [
    path("ideas/", BootcampIdeasListView.as_view(), name="bootcamp-ideas"),
    path("<int:idea_id>/decision/",BootcampDecisionView.as_view(),name="bootcamp-decision"),
    path("end-camp/<int:season_id>/", EndBootcampSessionsView.as_view(), name="end-camp"),
]