from django.urls import path
from .views import IdeaListAPIView, IdeaDetailAPIView

urlpatterns = [
    path("", IdeaListAPIView.as_view(), name="admin-idea-list"),
    path("<int:idea_id>/", IdeaDetailAPIView.as_view(), name="admin-idea-detail"),
]