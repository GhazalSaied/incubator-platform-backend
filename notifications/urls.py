from django.urls import path
from .views import (
    MyNotificationsAPIView,
    MarkNotificationAsReadAPIView,
    MarkAllNotificationsReadAPIView,
)

urlpatterns = [
    path("", MyNotificationsAPIView.as_view()),
    path("<int:notification_id>/read/", MarkNotificationAsReadAPIView.as_view()),
    path("read-all/", MarkAllNotificationsReadAPIView.as_view()),
]