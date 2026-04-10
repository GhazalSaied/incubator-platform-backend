from django.urls import path
from .views import (AssignmentDashboardAPIView,AvailableEvaluatorsView,AssignEvaluatorsToIdeaView,MeetingDashboardAPIView,IdeaEvaluatorsAPIView,SetMeetingAPIView)

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
]
    
