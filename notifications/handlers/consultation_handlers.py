from core.events import EventBus
from notifications.services.notification_service import NotificationService


def consultation_requested_handler(payload):

    consultation = payload["consultation"]

    NotificationService.send(
        user=consultation.volunteer.user,
        event_name=payload["event_name"],
        obj=consultation,
        actor=payload.get("actor"),
        extra=payload.get("action"),  
        action_url="/api/volunteers/consultations/",
        target_role="VOLUNTEER"
    )

def consultation_accepted_handler(payload):
    consultation = payload.get("consultation")
    if not consultation:
        return
    NotificationService.send(
        user=consultation.requester,
        event_name="consultation_accepted",
        obj=consultation,
        actor=payload.get("actor"),
        target_role="INCUBATOR" )


def consultation_rejected_handler(payload):
    consultation = payload.get("consultation")
    if not consultation:
        return
    NotificationService.send(
        user=consultation.requester,
        event_name="consultation_rejected",
        obj=consultation,
        actor=payload.get("actor"),
        action_url="/api/volunteers/consultants/",
        target_role="INCUBATOR" )

EventBus.register("consultation_requested", consultation_requested_handler)
EventBus.register("consultation_accepted", consultation_accepted_handler)
EventBus.register("consultation_rejected", consultation_rejected_handler)