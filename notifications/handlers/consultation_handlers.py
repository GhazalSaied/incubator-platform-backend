from core.events import EventBus
from notifications.services.notification_service import NotificationService


def consultation_requested_handler(payload):

    consultation = payload["consultation"]

    NotificationService.send(
        user=consultation.volunteer.user,
        event_name=payload["event_name"],
        obj=consultation,
        action_url=payload.get("action_url"),
        target_role="VOLUNTEER"
    )


def consultation_decided_handler(payload):

    consultation = payload["consultation"]

    NotificationService.send(
        user=consultation.requester,
        event_name=payload["event_name"],
        obj=consultation,
        extra=payload.get("action"),  
        action_url=payload.get("action_url"),
        target_role="IDEA_OWNER"
    )


EventBus.register("consultation_requested", consultation_requested_handler)
EventBus.register("consultation_decided", consultation_decided_handler)