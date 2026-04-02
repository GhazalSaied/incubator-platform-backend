from django.urls import path
from .views.seasons import SeasonCreateView,SeasonPublishView,CloseSeasonAPIView,SeasonListAPIView, SeasonDetailAPIView
from incubator_admin.views.idea_form import IdeaFormCreateView
from incubator_admin.views.form_question import FormQuestionListCreateView,FormQuestionDetailView
from incubator_admin.views.form_choice import (FormQuestionChoiceListCreateView,FormQuestionChoiceDetailView)
from incubator_admin.views.ideas import IdeaListAPIView,IdeaDetailAPIView
from incubator_admin.views.bootcamp_session import  BootcampSessionCreateView,BootcampSessionListView
from incubator_admin.views.bootcamp_attendance import IdeaAttendanceStatsView,SessionAttendanceListView,BootcampParticipantsView
from incubator_admin.views.bootcamp_decision import BootcampDecisionView,BootcampIdeasListView
from incubator_admin.views.bootcamp_absence import AbsenceRequestsListView,AbsenceDecisionView
from incubator_admin.views.evaluation import IdeasForEvaluationView,VolunteersListView,AssignEvaluatorsView


urlpatterns = [
    path('seasons/', SeasonCreateView.as_view()),
    path('seasons/<int:pk>/publish/', SeasonPublishView.as_view()),
    path('forms/', IdeaFormCreateView.as_view()),
    path('forms/<int:form_id>/questions/',FormQuestionListCreateView.as_view()),
    path('questions/<int:question_id>/choices/',FormQuestionChoiceListCreateView.as_view()),
    path('questions/<int:question_id>/choices/<int:choice_id>/',FormQuestionChoiceDetailView.as_view(),),
    path("seasons/<int:season_id>/close/",CloseSeasonAPIView.as_view(),name="admin-close-season"),
    path("forms/<int:form_id>/questions/<int:question_id>/",FormQuestionDetailView.as_view(),name="admin-form-question-detail"),
    path('seasons/', SeasonListAPIView.as_view()),
    path('seasons/list/', SeasonListAPIView.as_view()),
    path("seasons/<int:season_id>/",SeasonDetailAPIView.as_view(),name="admin-season-detail"),
    path("ideas/", IdeaListAPIView.as_view()),
    path("ideas/<int:idea_id>/", IdeaDetailAPIView.as_view()),
    path("bootcamp/sessions/", BootcampSessionCreateView.as_view()),
    path('bootcamp/sessions/list/', BootcampSessionListView.as_view()),
    path('bootcamp/sessions/<int:session_id>/attendance/',SessionAttendanceListView.as_view()),
    path('bootcamp/ideas/<int:idea_id>/absence-percentage/',IdeaAttendanceStatsView.as_view()), 
    path('bootcamp/decision/', BootcampDecisionView.as_view()),
    path('bootcamp/participants/', BootcampParticipantsView.as_view()),
    path('bootcamp/ideasList/', BootcampIdeasListView.as_view()),
    path('bootcamp/absence/', AbsenceRequestsListView.as_view()),
    path('bootcamp/absence/decision/', AbsenceDecisionView.as_view()),
    path("evaluation/ideas/", IdeasForEvaluationView.as_view()),
    path("ideas/<int:idea_id>/assign/", AssignEvaluatorsView.as_view()),
    path("volunteers/", VolunteersListView.as_view()),

]
