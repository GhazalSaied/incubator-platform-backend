from django.urls import path
from .views import (
    NotificationListAPIView,
    MarkNotificationAsReadAPIView,
    MarkAllNotificationsReadAPIView,
    NotificationBadgeAPIView,
)

urlpatterns = [
    path("", NotificationListAPIView.as_view()),#هي بتجيب all (اذا حطينا ?role= بترجع بس اشعارات الدور المحدد)
    path("<int:notification_id>/read/", MarkNotificationAsReadAPIView.as_view()),
    path("read-all/", MarkAllNotificationsReadAPIView.as_view()),
    path("badge/", NotificationBadgeAPIView.as_view()),
]