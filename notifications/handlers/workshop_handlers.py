from core.events import EventBus
from notifications.services.notification_service import NotificationService


def workshop_submitted_handler(workshop, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=workshop.created_by,
        event_name=event_name,
        obj=workshop,
        action_url=action_url,
        target_role="VOLUNTEER"
    )


def workshop_registered_handler(workshop, user, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=workshop.created_by,
        event_name=event_name,
        obj=workshop,
        actor=user,
        action_url=action_url,
        target_role="VOLUNTEER"
    )


EventBus.register("workshop_submitted", workshop_submitted_handler)
EventBus.register("workshop_registered", workshop_registered_handler)