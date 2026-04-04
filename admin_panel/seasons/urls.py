from django.urls import path
from .views import (
    SeasonCreateView,
    SeasonPublishView,
    CloseSeasonAPIView,
    SeasonListAPIView,
    SeasonDetailAPIView,
)

urlpatterns = [
    path("", SeasonListAPIView.as_view(), name="season-list"),
    path("create/", SeasonCreateView.as_view(), name="season-create"),
    path("<int:season_id>/", SeasonDetailAPIView.as_view(), name="season-detail"),
    path("<int:pk>/publish/", SeasonPublishView.as_view(), name="season-publish"),
    path("<int:season_id>/close/", CloseSeasonAPIView.as_view(), name="season-close"),
]