from django.urls import path
from .views import (
    VolunteerApplyAPIView,
    VolunteerProfileAPIView,
    VolunteerAvailabilityAPIView,
    VolunteerProfileUpdateAPIView,
)

urlpatterns = [
    path("apply/", VolunteerApplyAPIView.as_view()),
    path("me/", VolunteerProfileAPIView.as_view()),
    path("availability/", VolunteerAvailabilityAPIView.as_view()),
    path("me/update/", VolunteerProfileUpdateAPIView.as_view()),
]
