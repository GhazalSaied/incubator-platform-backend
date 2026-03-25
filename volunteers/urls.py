from django.urls import path
from .views import (
    VolunteerApplyAPIView,
    VolunteerProfileAPIView,
    VolunteerProfileUpdateAPIView,

    VolunteerAvailabilityAPIView,
    VolunteerAvailabilityCreateAPIView,
    VolunteerAvailabilityUpdateAPIView,
    VolunteerAvailabilityDeleteAPIView,

    MyConsultationRequestsAPIView,
    ConsultationRequestDecisionAPIView,
    CreateConsultationRequestAPIView,

    VolunteerDashboardAPIView,
)

urlpatterns = [
    # ================== VOLUNTEER APPLY ==================
    path("apply/", VolunteerApplyAPIView.as_view()),

    # ================== PROFILE ==================
    path("me/", VolunteerProfileAPIView.as_view()),
    path("me/update/", VolunteerProfileUpdateAPIView.as_view()),

    # ================== AVAILABILITY ==================
    path("availability/", VolunteerAvailabilityAPIView.as_view()),  # GET + PUT (bulk)

    path("availability/add/", VolunteerAvailabilityCreateAPIView.as_view()),
    path("availability/<int:availability_id>/update/", VolunteerAvailabilityUpdateAPIView.as_view()),
    path("availability/<int:availability_id>/delete/", VolunteerAvailabilityDeleteAPIView.as_view()),

    # ================== CONSULTATIONS ==================
    path("consultations/", MyConsultationRequestsAPIView.as_view()),
    path("consultations/<int:request_id>/decision/", ConsultationRequestDecisionAPIView.as_view()),
    path("consultations/create/", CreateConsultationRequestAPIView.as_view()),

    # ================== DASHBOARD ==================
    path("dashboard/", VolunteerDashboardAPIView.as_view()),
]