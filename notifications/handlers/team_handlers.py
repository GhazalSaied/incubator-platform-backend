from core.events import EventBus
from notifications.services.notification_service import NotificationService
from django.contrib.auth import get_user_model

User = get_user_model()


def team_request_created_handler(payload):

    team_request = payload.get("team_request")
    actor = payload.get("actor")

    if not team_request:
        return

    admins = User.objects.filter(
        is_staff=True,
        is_active=True
    )

    for admin in admins.iterator():

        NotificationService.send(
            user=admin,

            event_name="team_request_created",

            obj=team_request,

            actor=actor,

            target_role="ADMIN",

            action_url="/api/admin/volunteers/team-request-owners/"
        )


EventBus.register(
    "team_request_created",
    team_request_created_handler
)

def join_request_sent_handler(payload):
    join_request = payload["join_request"]

    NotificationService.send(
        user=join_request.volunteer.user,
        event_name=payload["event_name"],
        obj=join_request.idea,
        action_url="/api/volunteers/join-requests/",
        target_role="VOLUNTEER"
    )

def join_request_accepted_handler(payload):
    join_request = payload.get("join_request")
    if not join_request:
        return
    NotificationService.send(
        user=join_request.requester,
        event_name="join_request_accepted",
        obj=join_request,
        actor=payload.get("actor"),
        action_url="/api/ideas/team-dashboard/",
        target_role="INCUBATOR" )


def join_request_rejected_handler(payload):
    join_request = payload.get("join_request")
    if not join_request:
        return
    NotificationService.send(
        user=join_request.requester,
        event_name="join_request_rejected",
        obj=join_request,
        actor=payload.get("actor"),
        action_url="/api/ideas/suggested-volunteers/",
        target_role="INCUBATOR" )



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
        target_role="INCUBATOR"
    )






EventBus.register("join_request_accepted",join_request_accepted_handler)
EventBus.register("join_request_sent", join_request_sent_handler)
EventBus.register("team_completed", team_completed_handler)
EventBus.register("join_request_rejected", join_request_rejected_handler)