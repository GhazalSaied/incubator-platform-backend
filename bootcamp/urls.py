from django.urls import path
from .views import (
    OwnerBootcampSessionsAPIView,
    OwnerNextBootcampSessionAPIView,
    CreateBootcampAbsenceRequestAPIView,
    MyAssignedBootcampSessionsAPIView,
    BootcampSessionIdeasAPIView,
    CreateBootcampAttendanceAPIView,
)

urlpatterns = [

    path("owner-bootcamp/sessions/", OwnerBootcampSessionsAPIView.as_view()),
    path("owner-bootcamp/next-session/", OwnerNextBootcampSessionAPIView.as_view()),
    path("owner-bootcamp/absence-request/", CreateBootcampAbsenceRequestAPIView.as_view()),

    #=========================== TRAINER ====================================

    path("my-bootcamp-sessions/",MyAssignedBootcampSessionsAPIView.as_view()),
    path("bootcamp-sessions/<int:session_id>/ideas/",BootcampSessionIdeasAPIView.as_view()),
    path("bootcamp-sessions/<int:session_id>/attendance/", CreateBootcampAttendanceAPIView.as_view())
    
        
]