from core.events import EventBus
from notifications.services.notification_service import NotificationService


def join_request_sent_handler(payload):
    join_request = payload["join_request"]

    NotificationService.send(
        user=join_request.volunteer.user,
        event_name=payload["event_name"],
        obj=join_request.idea,
        action_url=payload.get("action_url"),
        target_role="VOLUNTEER"
    )

def join_request_accepted_handler(payload):
    jr = payload["join_request"]

    NotificationService.send(
        user=jr.requester,
        event_name=payload["event_name"],
        obj=jr.idea,
        actor=payload.get("actor"),
        action_url=payload.get("action_url"),
        target_role="IDEA_OWNER"
    )

def join_request_rejected_handler(payload):
    jr = payload["join_request"]

    NotificationService.send(
        user=jr.requester,
        event_name=payload["event_name"],
        obj=jr.idea,
        actor=payload.get("actor"),
        action_url=payload.get("action_url"),
        target_role="IDEA_OWNER"
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







EventBus.register("join_request_sent", join_request_sent_handler)
EventBus.register("team_completed", team_completed_handler)
EventBus.register("join_request_accepted",join_request_accepted_handler)
EventBus.register("join_request_rejected", join_request_rejected_handler)