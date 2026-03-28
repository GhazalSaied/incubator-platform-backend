from django.urls import path
from .views import (
    MyNotificationsAPIView,
    MarkNotificationAsReadAPIView,
    MarkAllNotificationsReadAPIView,
    UnreadNotificationsCountAPIView,
    NotificationBadgeAPIView,
)

urlpatterns = [
    path("", MyNotificationsAPIView.as_view()),
    path("<int:notification_id>/read/", MarkNotificationAsReadAPIView.as_view()),
    path("read-all/", MarkAllNotificationsReadAPIView.as_view()),
    path("unread-count/", UnreadNotificationsCountAPIView.as_view()),
    path("badge/", NotificationBadgeAPIView.as_view()),
]