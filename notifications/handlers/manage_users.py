from notifications.services.notification_service import NotificationService
from core.events import EventBus

def admin_manual_notification_handler(payload):

    user = payload.get("receiver")

    NotificationService.send(
        user=user,
        event_name="admin_manual_notification",
        extra=payload.get("extra"),
        target_role="USER"
    )
EventBus.register(
    "admin_manual_notification",
    admin_manual_notification_handler
)