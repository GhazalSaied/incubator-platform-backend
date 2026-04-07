from django.urls import path
from .views import (
    SessionAttendanceListView,
    IdeaAttendanceStatsView,
    BootcampParticipantsView,
)

urlpatterns = [
    #\\\\\\\\مراجعة الحضور لكل جلسة\\\\\\\\
    path("session/<int:session_id>/", SessionAttendanceListView.as_view(), name="session-attendance"),
    #\\\\\\\\مراجعة احصائيات الحضور لكل فكرة\\\\\\\\
    path("idea/<int:idea_id>/stats/", IdeaAttendanceStatsView.as_view(), name="idea-attendance-stats"),
    #\\\\\\\\مراجعة المقبولين في المعسكر\\\\\\\\
    path("participants/", BootcampParticipantsView.as_view(), name="bootcamp-participants"),
]