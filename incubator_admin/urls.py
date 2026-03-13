from django.urls import path
from .views.seasons import SeasonCreateView,SeasonPublishView,CloseSeasonAPIView
from incubator_admin.views.idea_form import IdeaFormCreateView
from incubator_admin.views.form_question import FormQuestionListCreateView,FormQuestionDetailView
from incubator_admin.views.form_choice import (FormQuestionChoiceListCreateView,FormQuestionChoiceDetailView)

urlpatterns = [
    path('seasons/', SeasonCreateView.as_view()),
    path('seasons/<int:pk>/publish/', SeasonPublishView.as_view()),
    path('forms/', IdeaFormCreateView.as_view()),
    path('forms/<int:form_id>/questions/',FormQuestionListCreateView.as_view()),
    path('questions/<int:question_id>/choices/',FormQuestionChoiceListCreateView.as_view()),
    path('questions/<int:question_id>/choices/<int:choice_id>/',FormQuestionChoiceDetailView.as_view(),),
    path("seasons/<int:season_id>/close/",CloseSeasonAPIView.as_view(),name="admin-close-season"),
    path("forms/<int:form_id>/questions/<int:question_id>/",FormQuestionDetailView.as_view(),name="admin-form-question-detail"),
]
