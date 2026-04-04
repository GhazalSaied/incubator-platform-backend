from celery import shared_task
from notifications.services.notification_service import NotificationService
from accounts.models import User


@shared_task
def send_notification_task(user_id, title, message, extra=None):

    user = User.objects.get(id=user_id)

    NotificationService.send(
        user=user,
        title=title,
        message=message,
        **(extra or {})
    )