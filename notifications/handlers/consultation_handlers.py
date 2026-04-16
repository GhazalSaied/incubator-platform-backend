from core.events import EventBus
from notifications.services.notification_service import NotificationService


def consultation_requested_handler(consultation, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=consultation.volunteer.user,
        event_name=event_name,
        obj=consultation,
        action_url=action_url,
        target_role="VOLUNTEER"
    )


def consultation_decided_handler(consultation, action, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=consultation.requester,
        event_name=event_name,
        obj=consultation,
        extra=action,  
        action_url=action_url,
        target_role="IDEA_OWNER"
    )


EventBus.register("consultation_requested", consultation_requested_handler)
EventBus.register("consultation_decided", consultation_decided_handler)