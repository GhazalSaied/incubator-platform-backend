from core.events import EventBus
from notifications.services.notification_service import NotificationService


def evaluation_invitation_sent_handler(invitation, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=invitation.user,
        event_name=event_name,
        obj=invitation,
        action_url=action_url,
        target_role="VOLUNTEER"
    )


def evaluation_invitation_accepted_handler(invitation, event_name, action_url=None, **kwargs):

    NotificationService.send(
        user=invitation.user,
        event_name=event_name,
        obj=invitation,
        action_url=action_url,
        target_role="VOLUNTEER"
    )


EventBus.register("evaluation_invitation_sent", evaluation_invitation_sent_handler)
EventBus.register("evaluation_invitation_accepted", evaluation_invitation_accepted_handler)