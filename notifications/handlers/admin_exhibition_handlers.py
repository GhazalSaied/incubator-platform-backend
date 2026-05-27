#create exhibition handler
from core.events import EventBus
from django.contrib.auth import get_user_model
from ideas.models import IdeaStatus,Idea
from notifications.services.notification_service import NotificationService


User = get_user_model()
def exhibition_scheduled_handler(payload):
    season_id = payload.get("season_id")
    exhibition_datetime = payload.get("exhibition_datetime")
    
    # إشعار جميع المستخدمين النشطين
    users = User.objects.filter(is_active=True,is_staff=False)

    for user in users.iterator():
        NotificationService.send(
            user=user,
            event_name="exhibition_scheduled",
            extra={
                "season_id": season_id,
                "exhibition_datetime": exhibition_datetime
            }
        )
EventBus.register("exhibition_scheduled", exhibition_scheduled_handler)




#\\\\\\\\\\\\\\\\هاندلر نشر نموذج المعرض\\\\\\\\\\\\\\\\
#الاشعار يصل فقط لاصحاب الافكار المتخرجة تخريج ايجابي 

def handle_exhibition_form_published(payload):

    season_id = payload.get("season_id")

    if not season_id:
        return

    # =========================
    # GET POSITIVE GRADUATED IDEAS
    # =========================

    ideas = (
        Idea.objects
        .select_related("owner")
        .filter(
            season_id=season_id,
            status=IdeaStatus.GRADUATED_POSITIVE
        )
    )

    # =========================
    # SEND NOTIFICATIONS
    # =========================

    for idea in ideas:

        NotificationService.send(
            user=idea.owner,
            event_name="exhibition_form_published",
            obj=idea,
            action_url="ideas/exhibition/dashboard/",
            target_role= "INCUBATOR"
        )
EventBus.register("exhibition_form_published",handle_exhibition_form_published )







#\\\\\\\\\\\\\\\\\\\\\القرار\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def handle_exhibition_submission_decided(payload):

    submission = payload.get("submission")
    decision = payload.get("decision")
    admin_message = payload.get("message")

    if not submission:
        return

    owner = submission.project.owner

    # =========================
    # TITLES
    # =========================

    if decision == "approved":

        title = "قبول بطاقة المعرض"

        base_message = (
            f"تم قبول بطاقة المعرض الخاصة "
            f"بمشروعك ({submission.project.title})."
        )

    else:

        title = "رفض بطاقة المعرض"

        base_message = (
            f"تم رفض بطاقة المعرض الخاصة "
            f"بمشروعك ({submission.project.title})."
        )

    # =========================
    # ADMIN MESSAGE
    # =========================

    if admin_message:

        final_message = (
            f"{base_message}\n\n"
            f"ملاحظات الإدارة:\n"
            f"{admin_message}"
        )

    else:
        final_message = base_message

    # =========================
    # SEND
    # =========================

    NotificationService.send(
        user=owner,
        title=title,
        message=final_message,
        related_object=submission.project,
        target_role= "INCUBATOR"
    )


EventBus.register(
    "exhibition_submission_decided",
    handle_exhibition_submission_decided
)