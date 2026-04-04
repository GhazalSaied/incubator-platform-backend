from django.urls import path, include

urlpatterns = [
    path("sessions/", include("admin_panel.bootcamp.sessions.urls")),
    path("attendance/", include("admin_panel.bootcamp.attendance.urls")),
    path("decisions/", include("admin_panel.bootcamp.decisions.urls")),
    path("absence/", include("admin_panel.bootcamp.absence.urls")),
]