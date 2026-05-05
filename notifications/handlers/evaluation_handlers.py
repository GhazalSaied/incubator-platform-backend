from core.events import EventBus
from notifications.services.notification_service import NotificationService


def evaluation_invitation_sent_handler(payload):
    invitation=payload["invitation"]


    NotificationService.send(
        user=invitation.user,
        event_name=payload["event_name"],
        obj=invitation,
        action_url=payload.get("action_url"),
        target_role="VOLUNTEER"
    )



def evaluation_invitation_accepted_handler(payload):
    invitation = payload["invitation"]
    actor = payload.get("actor")

    # مرسل الدعوة = الادمن 
    admin_user = invitation.created_by

    NotificationService.send(
        user=admin_user,
        event_name=payload["event_name"],
        obj=invitation,
        actor=actor,
        action_url=payload.get("action_url"),
        target_role="ADMIN"
    )


def evaluation_invitation_rejected_handler(payload):
    invitation = payload["invitation"]
    actor = payload.get("actor")

    # مرسل الدعوة = الادمن 
    admin_user = invitation.created_by

    NotificationService.send(
        user=admin_user,
        event_name=payload["event_name"],
        obj=invitation,
        actor=actor,
        action_url=payload.get("action_url"),
        target_role="ADMIN"
    )


EventBus.register("evaluation_invitation_sent", evaluation_invitation_sent_handler)
EventBus.register("evaluation_invitation_accepted",evaluation_invitation_accepted_handler)
EventBus.register("evaluation_invitation_rejected",evaluation_invitation_rejected_handler)
    
    
