from notifications.services.notification_service import NotificationService
from core.events import EventBus


def handle_meeting_scheduled(payload):

    idea = payload["idea"]
    assignments = payload["assignments"]
    meeting_datetime = payload["meeting_datetime"]

    data = {
        "idea": idea,
        "meeting_datetime": meeting_datetime
    }

    # -----------------------------
    # إشعار صاحب الفكرة
    # -----------------------------
    NotificationService.send(
        user=idea.owner,
        event_name="evaluation_meeting_scheduled_owner",
        extra=data,
        target_role="IDEA_OWNER"
    )

    # -----------------------------
    # إشعار المقيمين
    # -----------------------------
    notified_users = set()

    for assignment in assignments:

        if assignment.evaluator_id in notified_users:
            continue

        notified_users.add(assignment.evaluator_id)

        NotificationService.send(
            user=assignment.evaluator,
            event_name="evaluation_meeting_scheduled_evaluator",
            extra=data,
            target_role="EVALUATOR"
        )


EventBus.register(
    "evaluation_meeting_scheduled",
    handle_meeting_scheduled
)








#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def evaluation_accepted_handler(payload, actor=None):
    idea = payload.get("idea")
    message = payload.get("message", "تم قبول فكرتك في التقييم , مبروك! ..الان انت من المحتضنين")
    NotificationService.send(
        user=idea.owner,
        event_name="idea_accepted",
        obj=idea,
        extra={"message": message},
        actor=actor,
        
        target_role="IDEA_OWNER"
    )
    
    
    
EventBus.register("idea_accepted", evaluation_accepted_handler)


def evaluation_rejected_handler(payload, actor=None):

    idea = payload.get("idea")
    

    NotificationService.send(
        user=idea.owner,
        event_name="idea_rejected",
        obj=idea,
        actor=actor,
        action_url=f"/api/evaluations/ideas/{idea.id}/notes/",
        target_role="IDEA_OWNER"
    )

EventBus.register(
    "idea_rejected",
    evaluation_rejected_handler
)