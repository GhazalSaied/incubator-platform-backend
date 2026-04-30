#create exhibition handler
from core.events import EventBus
from django.contrib.auth import get_user_model
from ideas.models import IdeaStatus
from notifications.services.notification_service import NotificationService
User = get_user_model()
def exhibition_scheduled_handler(payload):
    season_id = payload.get("season_id")
    exhibition_datetime = payload.get("exhibition_datetime")
    
    # إشعار جميع المستخدمين النشطين
    users = User.objects.filter(is_active=True)

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
from ideas.models import Idea, IdeaStatus

from notifications.services.notification_service import (
    NotificationService
)


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
            obj=idea
        )
EventBus.register("exhibition_form_published",handle_exhibition_form_published )







#\\\\\\\\\\\\\\\\\\\\\القرار\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
from notifications.services.notification_service import (
    NotificationService
)


def handle_exhibition_submission_decided(payload):

    submission = payload.get("submission")
    decision = payload.get("decision")
    message = payload.get("message")

    if not submission:
        return

    owner = submission.project.owner

    # fallback messages
    if not message:

        if decision == "approved":
            message = (
                "تم قبول بطاقة المعرض الخاصة بمشروعك"
            )

        else:
            message = (
                "تم رفض بطاقة المعرض الخاصة بمشروعك"
            )

    title = (
        "قبول بطاقة المعرض"
        if decision == "approved"
        else "رفض بطاقة المعرض"
    )

    NotificationService.send(
        user=owner,
        title=title,
        message=message,
        related_object=submission.project
    )
EventBus.register(
            "exhibition_submission_decided",
            handle_exhibition_submission_decided
        )
