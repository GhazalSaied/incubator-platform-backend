from core.events import EventBus
from notifications.services.notification_service import NotificationService


def message_sent_handler(payload):

    NotificationService.send(
        user=payload["receiver"],
        event_name=payload["event_name"],
        actor=payload.get("sender"),
        obj=payload.get("conversation"),
        action_url=payload.get("action_url"),
        target_role="USER"
    )


EventBus.register("message_sent", message_sent_handler)