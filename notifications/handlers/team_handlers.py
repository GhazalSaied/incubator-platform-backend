from core.events import EventBus
from notifications.services.notification_service import NotificationService


def join_request_sent_handler(consultation, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=consultation.volunteer.user,
        event_name=event_name,
        obj=consultation,
        action_url=action_url,
        target_role="VOLUNTEER"
    )


EventBus.register("join_request_sent", join_request_sent_handler)