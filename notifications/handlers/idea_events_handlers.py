from core.events import EventBus
from notifications.services.notification_service import NotificationService
from ideas.models import IdeaStatus


def idea_status_changed_handler(payload):

    idea = payload.get("idea")
    new_status = payload.get("new_status")
    action_url = payload.get("action_url")

    if not idea:
        return

    if new_status == IdeaStatus.ACCEPTED:
        NotificationService.send(
            user=idea.owner,
            event_name=payload["event_name"],
            obj=idea,
            action_url=action_url,
            target_role="IDEA_OWNER"
        )

    elif new_status == IdeaStatus.REJECTED:
        NotificationService.send(
            user=idea.owner,
            event_name=payload["event_name"],
            obj=idea,
            action_url=action_url,
            target_role="IDEA_OWNER"
        )


EventBus.register("idea_status_changed", idea_status_changed_handler)



from django.contrib.auth import get_user_model
User = get_user_model()
def idea_submitted_handler(payload):
    idea = payload.get("idea")
    actor = payload.get("actor")
    if not idea:
        return
    admins = User.objects.filter( is_staff=True, is_active=True )
    for admin in admins.iterator():
        NotificationService.send(
            user=admin,
            event_name="idea_submitted",
            obj=idea,
            actor=actor,
            target_role="ADMIN",
            action_url=f"/api/admin/ideas/{idea.id}/details/"
            )
EventBus.register( "idea_submitted", idea_submitted_handler )



def exhibition_submission_created_handler(payload):
    submission = payload.get("submission")
    actor = payload.get("actor")
    if not submission:
        return
    admins = User.objects.filter( is_staff=True, is_active=True )
    for admin in admins.iterator():
        NotificationService.send(
            user=admin,
            event_name="exhibition_submission_created",
            obj=submission,
            actor=actor,
            target_role="ADMIN",
            action_url="/api/admin/exhibition/submissions/"
        )
EventBus.register( "exhibition_submission_created", exhibition_submission_created_handler )