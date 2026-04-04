from django.urls import path
from .views import (
    IdeaFormCreateView,
    FormQuestionListCreateView,
    FormQuestionDetailView,
    FormQuestionChoiceListCreateView,
    FormQuestionChoiceDetailView
)

urlpatterns = [
    # إنشاء فورم
    path("", IdeaFormCreateView.as_view(), name="form-create"),

    # أسئلة الفورم
    path("<int:form_id>/questions/", FormQuestionListCreateView.as_view(), name="question-list-create"),
    path("<int:form_id>/questions/<int:question_id>/", FormQuestionDetailView.as_view(), name="question-detail"),

    # خيارات السؤال
    path("<int:question_id>/choices/", FormQuestionChoiceListCreateView.as_view(), name="choice-list-create"),
    path("<int:question_id>/choices/<int:choice_id>/", FormQuestionChoiceDetailView.as_view(), name="choice-detail"),
]