from notifications.models import NotificationTemplate
from notifications.services.notification_service import NotificationService
from notifications.constants import NotificationTemplateCodes


def on_meeting_scheduled(*, idea, meeting_datetime, assignments):

    template = NotificationTemplate.objects.get(
        code=NotificationTemplateCodes.MEETING_SCHEDULED,
        is_active=True
    )

    users = set()

    users.add(idea.owner)

    for a in assignments:
        users.add(a.evaluator)

    context = {
        "idea_title": idea.title,
        "date": meeting_datetime.strftime("%Y-%m-%d %H:%M"),
    }

    for user in users:
        NotificationService.send_from_template(
            user=user,
            template=template,
            context=context,
            action_type="VIEW_IDEA",
            related_object=idea,
        )