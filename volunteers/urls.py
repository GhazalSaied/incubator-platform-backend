from django.urls import path
from .views import (
    VolunteerApplyAPIView,
    VolunteerProfileAPIView,
    VolunteerProfileUpdateAPIView,
    PublicVolunteerProfileAPIView,


   
    VolunteerAvailabilityCreateAPIView,
    VolunteerAvailabilityListAPIView,
    VolunteerAvailabilityDeleteAPIView,
    VolunteerVacationAPIView,
    DeleteVolunteerVacationAPIView,
    
    MyAllRequestsAPIView,
    MyConsultationRequestsAPIView,
    ConsultationRequestDecisionAPIView,
    CreateConsultationRequestAPIView,

    CreateJoinRequestAPIView,
    JoinRequestsAPIView,
    JoinRequestDecisionAPIView,
    JoinRequestDetailAPIView,


    CreateWorkshopAPIView,
    MyWorkshopsAPIView,
    MyWorkshopDetailAPIView,
    PublicWorkshopsAPIView,
    RegisterWorkshopAPIView,
    WorkshopDetailAPIView,
    NearestWorkshopAPIView,

    VolunteerDashboardAPIView,

    AssignedProjectsAPIView,
)

urlpatterns = [
    # ================== VOLUNTEER APPLY ==================
    path("apply/", VolunteerApplyAPIView.as_view()),

    # ================== PROFILE ==================
    path("me/", VolunteerProfileAPIView.as_view()),
    path("me/update/", VolunteerProfileUpdateAPIView.as_view()),
    path("public-me/<int:user_id>/",PublicVolunteerProfileAPIView.as_view()),

    # ================== AVAILABILITY ==================
    path("my-availability/", VolunteerAvailabilityListAPIView.as_view()),  # GET 

    path("availability/add/", VolunteerAvailabilityCreateAPIView.as_view()),
    path("availability/<int:availability_id>/delete/", VolunteerAvailabilityDeleteAPIView.as_view()),

    # ================== CONSULTATIONS ==================
    path("consultations/", MyConsultationRequestsAPIView.as_view()),
    path("consultations/create/", CreateConsultationRequestAPIView.as_view()),
    path("consultations/<int:request_id>/decision/", ConsultationRequestDecisionAPIView.as_view()),

    path("all_requests/",MyAllRequestsAPIView.as_view()), #GET > both consultations & join requests

    #================== JOIN =====================

    path("join/create/",CreateJoinRequestAPIView.as_view()),
    path("join-requests/",JoinRequestsAPIView.as_view()), #get
    path("join-requests/<int:request_id>/decision/",JoinRequestDecisionAPIView.as_view()),
    path("join-request-details/<int:request_id>/",JoinRequestDetailAPIView.as_view()),

    # ================== DASHBOARD ==================
    path("dashboard/", VolunteerDashboardAPIView.as_view()),

    # ================== ASSIGNED PROJECTS  ==================
    path("assigned-projects/", AssignedProjectsAPIView.as_view()),

    # ================ VACATIONS ======================

    path("vacations/",VolunteerVacationAPIView.as_view()),
    path("vacations/<int:vacation_id>/delete/",DeleteVolunteerVacationAPIView.as_view()),

    # ================= WORKSHOPS ====================

    path("workshops/create/",CreateWorkshopAPIView.as_view()),
    path("workshops/",MyWorkshopsAPIView.as_view()),
    path("workshop-details/<int:workshop_id>/",MyWorkshopDetailAPIView.as_view()),
    path("nearest-workshop/",NearestWorkshopAPIView.as_view()),
    path("public-workshops/",PublicWorkshopsAPIView.as_view()),
    path("public-workshops-details/<int:workshop_id>/", WorkshopDetailAPIView.as_view()),
    path("public-workshops/<int:workshop_id>/register/",RegisterWorkshopAPIView.as_view()),

]