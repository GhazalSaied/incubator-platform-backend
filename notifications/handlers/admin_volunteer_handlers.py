from core.events import EventBus
from notifications.services.template_service import TEMPLATES
from notifications.services.notification_service import NotificationService


def handle_volunteer_approved(event):
    user = event["user"]
    tpl = TEMPLATES["volunteer_approved"]

    NotificationService.send(
        user=user,
        event_name="volunteer_approved",
        title=tpl["title"],
        message=tpl["message"]
    )
EventBus.register("volunteer_approved", handle_volunteer_approved)
    
def handle_volunteer_rejected(event):
    user = event["user"]
    tpl = TEMPLATES["volunteer_rejected"]
    NotificationService.send(
        user=user,
        event_name="volunteer_rejected",
        title=tpl["title"],
        message=tpl["message"]
    )
    
EventBus.register("volunteer_rejected", handle_volunteer_rejected)   


def handle_evaluation_invitation_sent(event):

    invitation = event.payload.get("invitation")

    return [invitation.user]


EventBus.register("evaluation_invitation_sent", handle_evaluation_invitation_sent)


def evaluator_role_removed_handler(payload):

    user = payload.get("user")

    NotificationService.send(
        user=user,
        event_name="evaluator_role_removed",
        obj=user
    )
EventBus.register("evaluator_role_removed", evaluator_role_removed_handler)





def volunteers_suggested_handler(payload):

    idea = payload["idea"]

    NotificationService.send(
        user=idea.owner,
        event_name="volunteers_suggested",
        obj=payload,
        target_role="IDEA_OWNER"
    )
EventBus.register("volunteers_suggested", volunteers_suggested_handler) 





#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول ورشة عمل\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def workshop_approved_handler(payload):

    workshop = payload["workshop"]

    NotificationService.send(
        user=workshop.created_by,

        event_name="workshop_approved",

        obj=workshop,

        target_role="VOLUNTEER",

        action_url=payload.get("action_url"),

        related_object=workshop
    )
EventBus.register("workshop_approved", workshop_approved_handler)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\رفض ورشة عمل\\\\\\\\\\\\\\\\\\\\\\\\\\
def workshop_rejected_handler(payload):

    workshop = payload["workshop"]

    NotificationService.send(
        user=workshop.created_by,

        event_name="workshop_rejected",

        extra={
            "workshop": workshop,
            "rejection_reason": payload["rejection_reason"]
        },

        target_role="VOLUNTEER",

        action_url=payload.get("action_url"),

        related_object=workshop
    )
EventBus.register("workshop_rejected", workshop_rejected_handler)