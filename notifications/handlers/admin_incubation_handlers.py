from core.events import EventBus
from notifications.services.notification_service import (
    NotificationService
)


def handle_incubation_meeting_notification(payload):

    idea = payload.get("idea")
    assignments = payload.get("assignments")
    meeting_date = payload.get("meeting_date")

    if not idea:
        return

    # ==================================
    # OWNER
    # ==================================

    NotificationService.send(
        user=idea.owner,
        event_name="incubation_meeting_scheduled_owner",
        extra={
            "meeting_date": meeting_date
        }
    )


    # ==================================
    # MENTORS
    # ==================================

    for assignment in assignments:

        NotificationService.send(
            user=assignment.mentor,
            event_name="incubation_meeting_scheduled_mentor",
            extra={
                "meeting_date": meeting_date
            }
        )
EventBus.register(
    "incubation_meeting_scheduled_owner",
    handle_incubation_meeting_notification
)
        

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    

def handle_positive_graduation_notification(payload):

    idea = payload.get("idea")

    if not idea:
        return

    NotificationService.send(
        user=idea.owner,
        event_name="idea_Exhibition_graduated",
        obj=idea
    )
EventBus.register(
    "idea_EXhibition_graduated",
    handle_positive_graduation_notification
)


def handle_negative_graduation_notification(payload):

    idea = payload.get("idea")

    if not idea:
        return

    NotificationService.send(
        user=idea.owner,
        event_name="idea_graduated_negative",
        obj=idea
    )
EventBus.register(
    "idea_graduated_negative",  
    handle_negative_graduation_notification
)