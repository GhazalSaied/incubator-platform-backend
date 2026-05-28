from django.urls import path
from .views import GraduateIdeaView, GraduatedProjectsView, IncubationProjectsView,IdeaMentorsView,RemoveMentorsView,AssignMentorsView,ScheduleMeetingView,IdeaLatestReviewView

urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المشاريع المحتضنة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("projects/", IncubationProjectsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/mentors/", IdeaMentorsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\حذف مقيمين \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/mentors/remove/", RemoveMentorsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\تعيين مقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/mentors/assign/", AssignMentorsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\جدولة جلسة متابعة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/meetings/schedule/", ScheduleMeetingView.as_view()),
    #\\\\\\\\\\\\\\\\\عرض ملاحظات آخر جلسة متابعة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/latest-review/", IdeaLatestReviewView.as_view()),
    #\\\\\\\\\\\\\\\\\تخرج فكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:idea_id>/graduate/", GraduateIdeaView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("graduated-projects/",GraduatedProjectsView.as_view(),name="graduated-projects"),

]