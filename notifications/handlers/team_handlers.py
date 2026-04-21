from core.events import EventBus
from notifications.services.notification_service import NotificationService


def join_request_sent_handler(payload):
    consultation = payload["consultation"]

    NotificationService.send(
        user=consultation.volunteer.user,
        event_name=payload["event_name"],
        obj=consultation,
        action_url=payload.get("action_url"),
        target_role="VOLUNTEER"
    )

def team_completed_handler(payload):
    idea = payload.get("idea")
    action_url = payload.get("action_url")

    if not idea:
        return

    NotificationService.send(
        user=idea.owner,
        event_name=payload["event_name"],
        obj=idea,
        action_url=action_url,
        target_role="IDEA_OWNER"
    )


def team_member_removed_handler(payload):
    idea = payload.get("idea")
    member = payload.get("member")
    action_url = payload.get("action_url")

    if not idea or not member:
        return

    NotificationService.send(
        user=idea.owner,
        event_name=payload["event_name"],
        obj=idea,
        actor=member,
        action_url=action_url,
        target_role="IDEA_OWNER"
    )




EventBus.register("join_request_sent", join_request_sent_handler)
EventBus.register("team_completed", team_completed_handler)
EventBus.register("team_member_removed", team_member_removed_handler)