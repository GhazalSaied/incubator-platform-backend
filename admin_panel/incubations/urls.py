from django.urls import path
from .views import GraduateIdeaView, IncubationProjectsView,IdeaMentorsView,RemoveMentorsView,AvailableEvaluatorsView,AssignMentorsView,ScheduleMeetingView,IdeaDetailsAPIView,IdeaLatestReviewView

urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المشاريع المحتضنة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("projects/", IncubationProjectsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/mentors/", IdeaMentorsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\حذف مقيمين \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/mentors/remove/", RemoveMentorsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين المتاحين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("available-evaluators/", AvailableEvaluatorsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\تعيين مقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/mentors/assign/", AssignMentorsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\جدولة جلسة متابعة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/meetings/schedule/", ScheduleMeetingView.as_view()),
    #\\\\\\\\\\\\\\\\\عرض تفاصيل الفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:pk>/details/", IdeaDetailsAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\عرض ملاحظات آخر جلسة متابعة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/latest-review/", IdeaLatestReviewView.as_view()),
    #\\\\\\\\\\\\\\\\\تخرج فكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/graduate/", GraduateIdeaView.as_view()),

]