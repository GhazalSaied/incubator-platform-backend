#\\\\\\\\\\\\\\\\\\\\\\\bootcamp\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



from notifications.services.notification_service import NotificationService
from core.events import EventBus    
from ideas.models import Idea, IdeaStatus

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
    
EventBus.register("absence_decision_made", handle_absence_notification) 
    
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
            obj=session,
            target_role="VOLUNTEER"
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
            target_role="IDEA_OWNER",
            extra=idea
        )
        
EventBus.register("bootcamp_session_created", handle_bootcamp_session_created)






#\\\\\\\\\\\\\\\\\\\\\\\\\\decision\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def handle_bootcamp_decision_notification(payload):
    idea = payload["idea"]
    decision = payload["decision"]
    actor = payload.get("actor")
    

    # 🎯 اختيار template حسب القرار
    if decision == "accepted":
        event_name = "idea_approved"
    else:
        event_name = "idea_rejected"

    NotificationService.send(
        user=idea.owner,
        event_name=event_name,
        obj=idea,
        actor=actor,
        target_role="IDEA_OWNER"
    )
EventBus.register("bootcamp_decision_made", handle_bootcamp_decision_notification)


#\\\\\\\\\\\\\\\\\\\\\\\\\\اعلان انتهاء جلسات المعسكر \\\\\\\\\\\\\\\\\\\\\

def handle_bootcamp_ended(payload):
    idea_ids = payload["idea_ids"]
    actor_id = payload.get("actor_id")

    ideas = Idea.objects.filter(id__in=idea_ids).select_related("owner")

    for idea in ideas:
        NotificationService.send(
            user=idea.owner,
            event_name="bootcamp_sessions_ended",
            obj=idea
        )
EventBus.register("bootcamp_sessions_ended", handle_bootcamp_ended)