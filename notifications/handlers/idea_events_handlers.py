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