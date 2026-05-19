from core.events import EventBus
from notifications.services.notification_service import NotificationService
from django.contrib.auth import get_user_model
from ideas.models import IdeaStatus

User = get_user_model()


def season_published_handler(payload):

    season = payload.get("season")

    action_url = payload.get("action_url")

    users = User.objects.filter(
        is_active=True
    )

    for user in users.iterator():

        NotificationService.send(
            user=user,

            event_name="season_published",

            obj=season,

            action_url=action_url,

            target_role="USER"
        )


EventBus.register("season_published",season_published_handler)







