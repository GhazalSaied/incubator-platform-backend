from core.events import EventBus
from notifications.services.notification_service import NotificationService


def account_suspended_handler(user, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=user,
        event_name=event_name,
        action_url=action_url,
        target_role="USER"
    )


def admin_reply_sent_handler(user, message, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=user,
        event_name=event_name,
        obj=message,
        action_url=action_url,
        target_role="USER"
    )


EventBus.register("account_suspended", account_suspended_handler)
EventBus.register("admin_reply_sent", admin_reply_sent_handler)