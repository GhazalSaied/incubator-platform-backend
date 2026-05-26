from core.events import EventBus
from notifications.services.template_service import TEMPLATES
from notifications.services.notification_service import NotificationService


def handle_volunteer_approved(event):

    user = event["user"]
    tpl = TEMPLATES["volunteer_approved"]

    NotificationService.send(
        user=user,
        title=tpl["title"],
        message=tpl["message"](user),
        target_role="VOLUNTEER",
        action_url="/api/volunteers/me/"
    )

EventBus.register(
    "volunteer_approved",
    handle_volunteer_approved
)
    
def handle_volunteer_rejected(event):

    user = event["user"]
    tpl = TEMPLATES["volunteer_rejected"]

    NotificationService.send(
        user=user,
        title=tpl["title"],
        message=tpl["message"](user),
        target_role="VOLUNTEER",
        action_url=None
    )

EventBus.register(
    "volunteer_rejected",
    handle_volunteer_rejected
)

def handle_evaluation_invitation_sent(payload):

    invitation = payload.get("invitation")

    if not invitation:
        return

    NotificationService.send(
        user=invitation.user,
        event_name="evaluation_invitation_sent",
        obj=invitation,
        target_role="VOLUNTEER",
        action_url=f"/api/evaluations/invitation-details/{invitation.id}/"
    )

EventBus.register(
    "evaluation_invitation_sent",
    handle_evaluation_invitation_sent
)




def volunteers_suggested_handler(payload):

    idea = payload["idea"]

    NotificationService.send(
        user=idea.owner,
        event_name="volunteers_suggested",
        obj=payload,
        target_role="INCUBATOR",
        action_url="/api/ideas/suggested-volunteers/"
    )
EventBus.register("volunteers_suggested", volunteers_suggested_handler) 





#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول ورشة عمل\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
from django.contrib.auth import get_user_model

User = get_user_model()


def workshop_approved_handler(payload):

    workshop = payload["workshop"]

    # إشعار صاحب الورشة
    NotificationService.send(
        user=workshop.created_by,
        event_name="workshop_approved",
        obj=workshop,
        target_role="VOLUNTEER",
        related_object=workshop
    )

    # إشعار كل المستخدمين
    users = User.objects.filter(is_active=True,is_staff=False).exclude(id=workshop.created_by_id)

    for user in users.iterator():
        NotificationService.send(
            user=user,
            event_name="new_workshop_published",
            obj=workshop,
            action_url=f"/api/ideas/public-workshops-details/{workshop.id}/",
            related_object=workshop
        )


EventBus.register("workshop_approved", workshop_approved_handler)


def workshop_rejected_handler(payload):

    workshop = payload["workshop"]
    rejection_reason = payload["rejection_reason"]

    NotificationService.send(
        user=workshop.created_by,
        event_name="workshop_rejected",
        obj=workshop,
        extra={
            "rejection_reason": rejection_reason
        },
        target_role="VOLUNTEER",
        related_object=workshop
    )


EventBus.register("workshop_rejected", workshop_rejected_handler)