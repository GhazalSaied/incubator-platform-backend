from notifications.services.template_service import TEMPLATES
from notifications.services import NotificationService


def handle_volunteer_approved(event):
    user = event["user"]
    tpl = TEMPLATES["volunteer_approved"]

    NotificationService.send(
        user=user,
        title=tpl["title"],
        message=tpl["message"]
    )