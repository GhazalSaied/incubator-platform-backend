from core.events import EventBus
from notifications.services.notification_service import NotificationService


def workshop_submitted_handler(payload):
    workshop = payload["workshop"]

    NotificationService.send(
        user=workshop.created_by,
        event_name=payload["event_name"],
        obj=workshop,
        action_url=payload.get("action_url"),
        target_role="VOLUNTEER"
    )


def workshop_registered_handler(payload):
    workshop = payload["workshop"]

    NotificationService.send(
        user=workshop.created_by,
        event_name=payload["event_name"],
        obj=workshop,
        actor=payload.get("user"),
        action_url=payload.get("action_url"),
        target_role="VOLUNTEER"
    )


EventBus.register("workshop_submitted", workshop_submitted_handler)
EventBus.register("workshop_registered", workshop_registered_handler)