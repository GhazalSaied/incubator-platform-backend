from django.urls import path
from .views import (
    SessionAttendanceListView,
    IdeaAttendanceStatsView,
    BootcampParticipantsView,
)

urlpatterns = [
    path("session/<int:session_id>/", SessionAttendanceListView.as_view(), name="session-attendance"),
    path("idea/<int:idea_id>/stats/", IdeaAttendanceStatsView.as_view(), name="idea-attendance-stats"),
    path("participants/", BootcampParticipantsView.as_view(), name="bootcamp-participants"),
]