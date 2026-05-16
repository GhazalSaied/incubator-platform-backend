from notifications.services.notification_service import (
    NotificationService
)

from core.events import EventBus
def admin_broadcast_notification_handler(payload):

    users = payload["users"]

    message = payload["message"]

    action_url = payload.get("action_url")

    for user in users:

        NotificationService.send(
            user=user,

            event_name="ADMIN_BROADCAST_NOTIFICATION",

            extra={
                "message": message
            },

            action_url=action_url,

            notification_type="INFO",

            target_role="USER"
        )
        
EventBus.register(
    "ADMIN_BROADCAST_NOTIFICATION",
    admin_broadcast_notification_handler
)