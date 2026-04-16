from core.events import EventBus
from notifications.services.notification_service import NotificationService


def message_sent_handler(sender, receiver, conversation, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=receiver,
        event_name=event_name,
        actor=sender,
        obj=conversation,
        action_url=action_url,
        target_role="USER"
    )


EventBus.register("message_sent", message_sent_handler)