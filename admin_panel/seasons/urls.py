from django.urls import path
from .views import (
    CloseSubmissionAPIView,
    CreateSeasonAPIView,
    PublishSeasonAPIView,
    SeasonListAPIView,
    SeasonDetailsAPIView
)

urlpatterns = [
    path("", SeasonListAPIView.as_view(), name="season-list"),
    path("create/", CreateSeasonAPIView.as_view(), name="season-create"),
    path("<int:pk>/", SeasonDetailsAPIView.as_view(), name="season-detail"),
    path("<int:pk>/publish/", PublishSeasonAPIView.as_view(), name="season-publish"),
    path("<int:season_id>/close-submissions/",CloseSubmissionAPIView.as_view())
]