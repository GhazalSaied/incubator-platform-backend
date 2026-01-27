from django.urls import path
from .views import (
    VolunteerApplyAPIView,
    VolunteerProfileAPIView,
    VolunteerAvailabilityAPIView,
    VolunteerProfileUpdateAPIView,VolunteerAvailabilityCreateAPIView,
    VolunteerAvailabilityUpdateAPIView , VolunteerAvailabilityDeleteAPIView,
    MyConsultationRequestsAPIView,ConsultationRequestDecisionAPIView,
)

urlpatterns = [
    path("apply/", VolunteerApplyAPIView.as_view()),
    path("me/", VolunteerProfileAPIView.as_view()),
    path("availability/", VolunteerAvailabilityAPIView.as_view()),
    path("me/update/", VolunteerProfileUpdateAPIView.as_view()),
    path("availability/", VolunteerAvailabilityCreateAPIView.as_view()),
    path("availability/<int:availability_id>/update/", VolunteerAvailabilityUpdateAPIView.as_view()),
    path("availability/<int:availability_id>/delete/", VolunteerAvailabilityDeleteAPIView.as_view()),
    path("consultations/", MyConsultationRequestsAPIView.as_view()),
    path("consultations/<int:request_id>/decision/",ConsultationRequestDecisionAPIView.as_view()),
        
        
]
