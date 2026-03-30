from django.urls import path
from .views import (
    MyBootcampSessionsAPIView,
    NextSessionAPIView,
    CreateAbsenceRequestAPIView,
)

urlpatterns = [

    path("sessions/", MyBootcampSessionsAPIView.as_view()),
    path("next-session/", NextSessionAPIView.as_view()),
    path("absence/", CreateAbsenceRequestAPIView.as_view()),
        
]