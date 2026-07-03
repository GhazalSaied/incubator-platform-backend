from core.events import EventBus
from notifications.services.notification_service import NotificationService
from accounts.models import User


def workshop_submitted_handler(payload):
    workshop = payload["workshop"]
    admins = User.objects.filter( is_staff=True )
    for admin in admins:
        NotificationService.send(
            user=admin, event_name="workshop_submitted",
            obj=workshop,
            actor=payload.get("actor"),
            action_url= "/api/workshops/",
            target_role="ADMIN" )

def workshop_registered_handler(payload):
    workshop = payload["workshop"]
    NotificationService.send(
        user=workshop.created_by,
        event_name="workshop_registered",
        obj=workshop,
        actor=payload.get("actor"),
        action_url=f"/api/volunteers/workshop-details/{workshop.id}/",
        extra={ "registrations_count": payload.get("registrations_count") },
        target_role="VOLUNTEER" )



EventBus.register("workshop_submitted", workshop_submitted_handler)
EventBus.register("workshop_registered", workshop_registered_handler)