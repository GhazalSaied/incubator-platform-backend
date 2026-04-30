from core.events import EventBus
from notifications.services.notification_service import NotificationService
from django.contrib.auth import get_user_model
from ideas.models import IdeaStatus

User = get_user_model()


def season_published_handler(payload, actor=None):
    season = payload.get("season")
    users = User.objects.filter(is_active=True)  # ✅ optimization

    for user in users.iterator():  # ✅ مهم جداً
        NotificationService.send(
            user=user,
            event_name="season_published",
            obj=season,
            actor=actor
        )

EventBus.register("season_published", season_published_handler)



def submission_closed_handler(payload):
    season = payload.get("season")

    users = User.objects.filter(is_active=True)  # ✅ optimization

    for user in users.iterator():
        NotificationService.send(
            user=user,
            event_name="submission_closed",
            obj=season,
            
        )


EventBus.register("submission_closed", submission_closed_handler)





#\\\\\\\\\\\\\\\\\\\\\\\bootcamp\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def handle_absence_notification(payload):
    absence = payload["absence"]
    decision = payload["decision"]

    # تحديد event_name حسب القرار
    if decision == "approved":
        event_name = "absence_approved"
    elif decision == "warned":
        event_name = "absence_warned"
    else:
        return

    NotificationService.send(
        user=absence.idea.owner,
        event_name=event_name,
        obj=absence,
        related_object=absence,
        
    )
    
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\اضافة جلسة \\\\\\\\\\\\\\\\\
def handle_bootcamp_session_created(payload):
    session = payload["session"]

    # ----------------------------
    # 1. Notify trainer
    # ----------------------------
    if session.trainer:
        NotificationService.send(
            user=session.trainer,
            event_name="bootcamp_session_assigned",
            obj=session
        )

    # ----------------------------
    # 2. Notify all BOOTCAMP ideas
    # ----------------------------
    from ideas.models import Idea

    ideas = Idea.objects.filter(status=IdeaStatus.BOOTCAMP)

    for idea in ideas:
        NotificationService.send(
            user=idea.owner,
            event_name="bootcamp_session_scheduled",
            obj=session,
            extra=idea
        )