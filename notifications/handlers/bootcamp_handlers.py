#\\\\\\\\\\\\\\\\\\\\\\\bootcamp\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



from notifications.services.notification_service import NotificationService
from core.events import EventBus    
from ideas.models import Idea, IdeaStatus



def bootcamp_started_handler(payload):

    season = payload.get("season")

    ideas = (
        Idea.objects
        .filter(
            season=season
        )
        .select_related("owner")
        .distinct()
    )

    sent_users = set()

    for idea in ideas:

        owner = idea.owner

        if not owner:
            continue

        if owner.id in sent_users:
            continue

        sent_users.add(owner.id)

        NotificationService.send(
            user=owner,
            event_name="bootcamp_started",
            obj=season,
            target_role="IDEA_OWNER",
        )


EventBus.register("bootcamp_started",bootcamp_started_handler)

def handle_absence_notification(payload):

    absence = payload["absence"]
    decision = payload["decision"]

    # =====================================
    # Determine Notification Type
    # =====================================

    if decision == "approved":
        event_name = "absence_approved"

    elif decision == "warned":
        event_name = "absence_warned"

    else:
        return

    # =====================================
    # Send Notification
    # =====================================

    NotificationService.send(
        user=absence.idea.owner,
        event_name=event_name,
        obj=absence,
        related_object=absence,
        target_role="IDEA_OWNER"
    )


EventBus.register(
    "absence_decision_made",
    handle_absence_notification
)
#\\\\\\\\\\\\\\\\\\\\\\\\اضافة جلسة \\\\\\\\\\\\\\\\\
def handle_bootcamp_session_created(payload):

    session = payload["session"]

    # =====================================
    # 1. Notify Trainer
    # =====================================

    if session.trainer:

        NotificationService.send(
            user=session.trainer,
            event_name="bootcamp_session_assigned",
            obj=session,
            target_role="VOLUNTEER"
        )

    # =====================================
    # 2. Notify Bootcamp Ideas Owners
    # =====================================

    ideas = (
        Idea.objects
        .filter(
            season=session.phase.season,
            status=IdeaStatus.BOOTCAMP
        )
        .select_related("owner")
    )

    sent_users = set()

    for idea in ideas:

        if not idea.owner:
            continue

        # منع التكرار
        if idea.owner.id in sent_users:
            continue

        sent_users.add(idea.owner.id)

        NotificationService.send(
            user=idea.owner,
            event_name="bootcamp_session_scheduled",
            obj=session,
            target_role="IDEA_OWNER"
        )


EventBus.register("bootcamp_session_created",handle_bootcamp_session_created)






#\\\\\\\\\\\\\\\\\\\\\\\\\\decision\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def handle_bootcamp_decision_notification(payload):

    idea = payload["idea"]
    decision = payload["decision"]
    actor = payload.get("actor")

    # =====================================
    # Determine Notification Event
    # =====================================

    if decision == "accepted":
        event_name = "idea_approved"

    elif decision == "rejected":
        event_name = "idea_rejected"

    else:
        return

    # =====================================
    # Send Notification
    # =====================================

    NotificationService.send(
        user=idea.owner,
        event_name=event_name,
        obj=idea,
        actor=actor,
        target_role="IDEA_OWNER"
    )


EventBus.register(
    "bootcamp_decision_made",
    handle_bootcamp_decision_notification
)

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


#//////////////////////// اشعار طلب الغياب للادارة /////////////////////////


from django.contrib.auth import get_user_model

User = get_user_model()
def bootcamp_absence_request_submitted_handler(payload):

    print("🔥🔥 ABSENCE HANDLER STARTED")

    absence_request = payload.get("absence_request")
    actor = payload.get("actor")

    print("ABSENCE REQUEST:", absence_request)
    print("ACTOR:", actor)

    if not absence_request:
        print("❌ NO ABSENCE REQUEST")
        return

    season_id = absence_request.session.phase.season.id

    print("✅ SEASON ID:", season_id)

    admins = User.objects.filter(
        is_staff=True,
        is_active=True
    )

    print("👑 ADMINS:", list(admins.values_list("id", "email")))

    for admin in admins.iterator():

        print("📨 SENDING TO ADMIN:", admin.id)

        NotificationService.send(
            user=admin,
            event_name="bootcamp_absence_request_submitted",
            obj=absence_request,
            actor=actor,
            action_url=f"/admin/camp-management/{season_id}",
        )

        print("✅ NOTIFICATION SENT TO:", admin.id)
EventBus.register("bootcamp_absence_request_submitted", bootcamp_absence_request_submitted_handler)
