from django.urls import path
from .views import (
    MyNotificationsAPIView,
    MarkNotificationAsReadAPIView,
    MarkAllNotificationsReadAPIView,
    NotificationBadgeAPIView,
)

urlpatterns = [
    path("", MyNotificationsAPIView.as_view()),
    path("<int:notification_id>/read/", MarkNotificationAsReadAPIView.as_view()),
    path("read-all/", MarkAllNotificationsReadAPIView.as_view()),
    path("badge/", NotificationBadgeAPIView.as_view()),
]