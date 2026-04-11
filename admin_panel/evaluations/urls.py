from django.urls import path
from .views import (AssignmentDashboardAPIView,AvailableEvaluatorsView,AssignEvaluatorsToIdeaView,MeetingDashboardAPIView,IdeaEvaluatorsAPIView, PublishCriteriaView,SetMeetingAPIView,CriteriaListCreateView,
                    CriteriaUpdateView,CriteriaToggleActiveView,CriteriaPreviewView,PublishCriteriaView,EvaluationResultsView,EvaluationDetailsView,AcceptIdeaView,RejectIdeaView)

urlpatterns = [
    #\\\عرض المشاريع المقبولة بالمعسكر لتعيين مقيمين\\\\\\\\\\
    path("assignment-dashboard/",AssignmentDashboardAPIView.as_view(),name="assignment-dashboard"),
    #\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين المتاحين لتعيينهم على الافكار\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("available-evaluators/",AvailableEvaluatorsView.as_view(),name="available-evaluators"),
    #\\\\\\\\\\\\\\\\\\\\\\\تعيين مقيمين على فكرة معينة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("assign-evaluators/",AssignEvaluatorsToIdeaView.as_view(),name="assign-evaluators"),
    #\\\\\\\\\\\\\\\\\\\\\\\عرض المشاريع مع المقيمين المعينين لها في جدول تحديد موعد اللجنة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("meeting-dashboard/",MeetingDashboardAPIView.as_view(),name="meeting-dashboard"),
    #\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين المعينين على فكرة معينة في جدول تحديد موعد اللجنة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("idea-evaluators/<int:idea_id>/",IdeaEvaluatorsAPIView.as_view(),name="idea-evaluators"),
    #\\\\\\\\\\\\\\\\\\\\\\\تحديد موعد اللجنة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("set-meeting/",SetMeetingAPIView.as_view(),name="set-meeting"),
    #\\\\\\\\\\\\\\\\\\\\\\\انشاء معيار تقييم\\\\\\\\\\\\\\\\\\\\\\
    path("criteria/",CriteriaListCreateView.as_view(),name="criteria-list-create"),
    #\\\\\\\\\\\\\\\\\\\\\\\تعديل معيار تقييم\\\\\\\\\\\\\\\\\\\\\\
    path("criteria/<int:pk>/",CriteriaUpdateView.as_view(),name="criteria-update"),
    #\\\\\\\\\\\\\\\\\\\\\\\تفعيل/تعطيل معيار تقييم\\\\\\\\\\\\\\\\\\\\\\
    path("criteria/<int:pk>/toggle-active/",CriteriaToggleActiveView.as_view(),name="criteria-toggle-active"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\معاينة معايير التقييم\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("criteria/preview/",CriteriaPreviewView.as_view(),name="criteria-preview"),
    #\\\\\\\\\\\\\\\\\\\\\نشر نموذج التقييم\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("criteria/publish/",PublishCriteriaView.as_view(),name="criteria-publish"),
    #\\\\\\\\\\\\\\\\\\\\\جدول عرض نتائج التقييمات\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("evaluation-results/",EvaluationResultsView.as_view(),name="evaluation-results"),
    #\\\\\\\\\\\\\\\\\\\\\عرض المقيمين مع ملاحظاتن\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("evaluation-details/<int:idea_id>/",EvaluationDetailsView.as_view(),name="evaluation-details"),
    #\\\\\\\\\\\\\\\\\\\\\قبول فكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("accept-idea/<int:idea_id>/",AcceptIdeaView.as_view(),name="accept-idea"),
    #\\\\\\\\\\\\\\\\\\\\\رفض فكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("reject-idea/<int:idea_id>/",RejectIdeaView.as_view(),name="reject-idea")

]
    
