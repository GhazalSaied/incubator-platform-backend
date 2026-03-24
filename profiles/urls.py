from django.urls import path
from .views import IdeaOwnerProfileAPIView

urlpatterns = [
    path(
        "idea-owner/",
        IdeaOwnerProfileAPIView.as_view(),
        name="idea-owner-profile"
    )
]
