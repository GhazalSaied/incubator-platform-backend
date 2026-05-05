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
     NextUpcomingSessionAPIView
)

urlpatterns = [
    path("idea/<int:idea_id>/evaluate/", EvaluationCreateUpdateAPIView.as_view()),
    path("idea/<int:idea_id>/submit/", EvaluationSubmitAPIView.as_view()),
    path("idea/<int:idea_id>/my/", MyEvaluationDetailAPIView.as_view()),
    path("respond-to-invitation/<int:invitation_id>/",RespondToInvitationAPIView.as_view()),
    path("my-assignments/", MyAssignmentsAPIView.as_view()),
    path("my-assignments_details/<int:assignment_id>/",AssignmentProjectDetailsAPIView.as_view()),
    path("evaluation-creteria/",EvaluationCriteriaAPIView.as_view()),
    path("invitation-details/<int:invitation_id>/",InvitationDetailsAPIView.as_view()),
    path("evaluation-form/<int:idea_id>/",EvaluationFormAPIView.as_view()),
    path("evaluation-notes/<int:idea_id>/",EvaluationNotesAPIView.as_view()),#post + get
    path("incubation-review/",IncubationReviewAPIView.as_view()),
    path("next-evaluation-session/", NextUpcomingSessionAPIView.as_view())





         
]
