from django.urls import path
from .views import (
    EvaluationCreateUpdateAPIView,
    EvaluationSubmitAPIView,
    MyEvaluationDetailAPIView,
    RespondToInvitationAPIView,
    MyAssignmentsAPIView,
    AssignmentProjectDetailsAPIView,
    EvaluationCriteriaAPIView,
    InvitationDetailsAPIView,
    EvaluationFormAPIView,
    EvaluationNotesAPIView,
    IncubationReviewAPIView,
    NextUpcomingSessionAPIView,
    IncubationLatestNotesAPIView,
    EvaluationSessionStatusAPIView,
    IncubationOverviewAPIView,
    NotesForIdeaOwnersAPIVIEW

)

urlpatterns = [

    #====================== EVALUATE ==================================
    path("idea/<int:idea_id>/evaluate/", EvaluationCreateUpdateAPIView.as_view()),
    path("idea/<int:idea_id>/submit/", EvaluationSubmitAPIView.as_view()),
    path("idea/<int:idea_id>/my/", MyEvaluationDetailAPIView.as_view()),
    path("evaluation-form/<int:idea_id>/",EvaluationFormAPIView.as_view()),
    path("evaluation-creteria/",EvaluationCriteriaAPIView.as_view()),

    #===================== INVITATION =============================
    path("respond-to-invitation/<int:invitation_id>/",RespondToInvitationAPIView.as_view()),
    path("invitation-details/<int:invitation_id>/",InvitationDetailsAPIView.as_view()),

    #================== ASSIGNMENTS =====================================
    path("my-assignments/", MyAssignmentsAPIView.as_view()),
    path("my-assignments_details/<int:assignment_id>/",AssignmentProjectDetailsAPIView.as_view()),
    
    
    #=========================== NOTES =====================================
    path("evaluation-notes/<int:idea_id>/",EvaluationNotesAPIView.as_view()),#post + get
    path("incubation-review/<int:idea_id>/",IncubationReviewAPIView.as_view()),
    path("incubation/<int:idea_id>/latest-notes/",IncubationLatestNotesAPIView.as_view()),

    #========================== PHASES IN INCUBATION PHASES TAB  ==========================
    path("ideas/<int:idea_id>/evaluation-session-status/",EvaluationSessionStatusAPIView.as_view()), #EVALUATION
    path("incubation/<int:idea_id>/overview/",IncubationOverviewAPIView.as_view()), #INCUBATION


    path("ideas/<int:idea_id>/notes/",NotesForIdeaOwnersAPIVIEW.as_view()),   
    path("next-upcoming-session/",NextUpcomingSessionAPIView.as_view()),  
]
