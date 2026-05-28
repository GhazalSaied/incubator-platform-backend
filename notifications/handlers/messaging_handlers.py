from core.events import EventBus
from notifications.services.notification_service import NotificationService


def message_sent_handler(payload):

    conversation = payload["conversation"]
    sender = payload["sender"]
    message = payload["message"]

    participants = (
        conversation.participants
        .exclude(user=sender)
        .select_related("user")
    )

    for participant in participants:

        NotificationService.send(
            user=participant.user,
            event_name="message_sent",
            obj=message,
            actor=sender,
            action_url=f"/messages/{conversation.id}/",
            target_role="USER",
        )


EventBus.register("message_sent", message_sent_handler)