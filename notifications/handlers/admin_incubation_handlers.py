from core.events import EventBus
from notifications.services.notification_service import (
    NotificationService
)


def handle_incubation_meeting_notification(payload):

    idea = payload.get("idea")
    assignments = payload.get("assignments", [])
    meeting_date = payload.get("meeting_date")

    if not idea:
        return

    formatted_date = meeting_date.strftime("%Y-%m-%d %H:%M")

    data = {
        "meeting_date": formatted_date,
        "idea_title": idea.title
    }

    # ==================================
    # OWNER
    # ==================================

    NotificationService.send(
        user=idea.owner,
        event_name="incubation_meeting_scheduled_owner",
        extra=data,
        target_role= "INCUBATOR"
    )

    # ==================================
    # MENTORS
    # ==================================

    for assignment in assignments:

        NotificationService.send(
            user=assignment.mentor.user,
            event_name="incubation_meeting_scheduled_mentor",
            extra=data,
            target_role= "EVALUATOR"
        )


EventBus.register(
    "incubation_meeting_scheduled",
    handle_incubation_meeting_notification
)
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    

def handle_positive_graduation_notification(payload):

    idea = payload.get("idea")

    if not idea:
        return

    NotificationService.send(
        user=idea.owner,
        event_name="idea_exhibition_graduated",
        obj=idea,
        target_role= "INCUBATOR"
    )


EventBus.register(
    "idea_exhibition_graduated",
    handle_positive_graduation_notification
)


def handle_negative_graduation_notification(payload):

    idea = payload.get("idea")

    if not idea:
        return

    NotificationService.send(
        user=idea.owner,
        event_name="idea_graduated_negative",
        obj=idea,
        target_role= "INCUBATOR"
    )


EventBus.register(
    "idea_graduated_negative",
    handle_negative_graduation_notification
)