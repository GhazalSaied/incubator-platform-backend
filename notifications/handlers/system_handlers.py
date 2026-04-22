from core.events import EventBus
from notifications.services.notification_service import NotificationService


def account_suspended_handler(payload):

    NotificationService.send(
        user=payload["user"],
        event_name=payload["event_name"],
        action_url=payload.get("action_url"),
        target_role="USER"
    )


def admin_reply_sent_handler(payload):

    NotificationService.send(
        user=payload["user"],
        event_name=payload["event_name"],
        obj=payload.get("message"),
        action_url=payload.get("action_url"),
        target_role="USER"
    )


EventBus.register("account_suspended", account_suspended_handler)
EventBus.register("admin_reply_sent", admin_reply_sent_handler)