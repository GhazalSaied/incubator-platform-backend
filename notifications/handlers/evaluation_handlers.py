from core.events import EventBus
from notifications.services.notification_service import NotificationService

def evaluation_invitation_accepted_handler(payload):

    invitation = payload.get("invitation")
    actor = payload.get("actor")

    if not invitation:
        return

    admin_user = invitation.created_by

    NotificationService.send(
        user=admin_user,

        event_name="evaluation_invitation_accepted",

        obj=invitation,

        actor=actor,

        target_role="ADMIN"
    )


EventBus.register(
    "evaluation_invitation_accepted",
    evaluation_invitation_accepted_handler
)


def evaluation_joined_committee_handler(payload):
    invitation = payload.get("invitation")
    if not invitation:
        return
    NotificationService.send(
        user=invitation.user,
        event_name="evaluation_joined_committee",
        obj=invitation,
        actor=payload.get("actor"),
        target_role="EVALUATOR" )
    
EventBus.register( "evaluation_joined_committee", evaluation_joined_committee_handler )
    
def evaluation_invitation_rejected_handler(payload):

    invitation = payload.get("invitation")
    actor = payload.get("actor")

    if not invitation:
        return

    admin_user = invitation.created_by

    NotificationService.send(
        user=admin_user,

        event_name="evaluation_invitation_rejected",

        obj=invitation,

        actor=actor,

        target_role="ADMIN"
    )


EventBus.register(
    "evaluation_invitation_rejected",
    evaluation_invitation_rejected_handler
)