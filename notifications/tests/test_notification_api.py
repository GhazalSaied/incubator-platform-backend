import pytest

from rest_framework.test import APIClient

from notifications.models import Notification


@pytest.mark.django_db
class TestNotificationAPI:

    def test_get_notifications(
        self,
        user,
    ):

        Notification.objects.create(
            user=user,
            title="Test",
            message="Hello",
        )

        client = APIClient()

        client.force_authenticate(user=user)

        response = client.get(
            "/api/notifications/"
        )

        assert response.status_code == 200

        assert len(response.data) == 1

    # -------------------------------------

    def test_notification_badge(
        self,
        user,
    ):

        Notification.objects.create(
            user=user,
            title="Test",
            message="Hello",
        )

        client = APIClient()

        client.force_authenticate(user=user)

        response = client.get(
            "/api/notifications/badge/"
        )

        assert response.status_code == 200

        assert response.data["unread_count"] == 1

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

        client = APIClient()

        client.force_authenticate(user=user)

        response = client.post(
            f"/api/notifications/{notification.id}/read/"
        )

        assert response.status_code == 200

        notification.refresh_from_db()

        assert notification.is_read is True