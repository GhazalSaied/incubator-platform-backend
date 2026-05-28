import pytest

from notifications.models import Notification
from notifications.services.notification_service import (
    NotificationService,
)


@pytest.mark.django_db
class TestNotificationService:

    def test_send_notification_creates_notification(
        self,
        user,
    ):

        notification = NotificationService.send(
            user=user,
            title="Test",
            message="Hello",
        )

        assert notification is not None

        assert Notification.objects.count() == 1

        notification.refresh_from_db()

        assert notification.title == "Test"
        assert notification.message == "Hello"
        assert notification.is_read is False

    # -------------------------------------

    def test_mark_notification_as_read(
        self,
        user,
    ):

        notification = Notification.objects.create(
            user=user,
            title="Test",
            message="Hello",
        )

        NotificationService.mark_as_read(
            user,
            notification.id,
        )

        notification.refresh_from_db()

        assert notification.is_read is True

    # -------------------------------------

    def test_mark_all_notifications_as_read(
        self,
        user,
    ):

        Notification.objects.create(
            user=user,
            title="1",
            message="1",
        )

        Notification.objects.create(
            user=user,
            title="2",
            message="2",
        )

        updated_count = (
            NotificationService.mark_all_as_read(
                user
            )
        )

        assert updated_count == 2

        assert (
            Notification.objects.filter(
                user=user,
                is_read=False,
            ).count()
            == 0
        )

    # -------------------------------------

    def test_get_unread_data(
        self,
        user,
    ):

        Notification.objects.create(
            user=user,
            title="1",
            message="1",
        )

        data = NotificationService.get_unread_data(
            user
        )

        assert data["unread_count"] == 1
        assert data["has_unread_notifications"] is True