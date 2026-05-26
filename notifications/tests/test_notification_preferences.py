import pytest

from notifications.models import (
    Notification,
    NotificationPreference,
)

from notifications.services.notification_service import (
    NotificationService,
)


@pytest.mark.django_db
class TestNotificationPreferences:

    def test_notification_blocked_by_preferences(
        self,
        user,
    ):

        NotificationPreference.objects.create(
            user=user,
            event_name="message_sent",
            role="USER",
            is_enabled=False,
        )

        NotificationService.send(
            user=user,
            event_name="message_sent",
            actor=user,
            target_role="USER",
        )

        assert Notification.objects.count() == 0