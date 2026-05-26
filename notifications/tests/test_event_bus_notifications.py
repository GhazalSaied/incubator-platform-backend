import pytest

from core.events import EventBus

from notifications.models import Notification


@pytest.mark.django_db
class TestEventBusNotifications:

    def test_event_bus_creates_notification(
        self,
        user,
    ):

        EventBus.emit(
            "account_suspended",
            actor=user,
            user=user,
        )

        assert (
            Notification.objects.count()
            >= 1
        )