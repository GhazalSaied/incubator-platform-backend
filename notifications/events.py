from core.events import EventBus
from notifications.services.template_service import TemplateService
from notifications.services.notification_service import NotificationService
from django.conf import settings
from notifications.tasks import send_notification_task

def idea_status_changed_listener(event):

    idea = event.payload["idea"]
    new_status = event.payload["new_status"]

    templates_map = {
        "submitted": "IDEA_SUBMITTED",
        "accepted": "IDEA_ACCEPTED",
        "rejected": "IDEA_REJECTED",
    }

    template_code = templates_map.get(new_status)

    if not template_code:
        return

    title, message = TemplateService.render(
        template_code,
        {
            "user_name": idea.owner.full_name,
            "idea_title": idea.title
        }
    )

    #  Sync / Async switch
    if settings.USE_ASYNC_TASKS:
       

        send_notification_task.delay(
            user_id=idea.owner.id,
            title=title,
            message=message
        )
    else:
        NotificationService.send(
            user=idea.owner,
            title=title,
            message=message
        )


EventBus.register("idea_status_changed", idea_status_changed_listener)