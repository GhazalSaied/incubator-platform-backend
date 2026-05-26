import pytest

from asgiref.sync import sync_to_async

from channels.testing import WebsocketCommunicator

from core.asgi import application

from notifications.services.notification_service import (
    NotificationService,
)


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestNotificationRealtime:

    async def test_notification_created_realtime(
        self,
        user,
        access_token,
    ):

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={access_token}",
        )

        try:

            connected, _ = await communicator.connect()

            assert connected is True

            # CREATE NOTIFICATION

            await sync_to_async(
                NotificationService.send
            )(
                user=user,
                title="Realtime Test",
                message="Hello Realtime",
            )

            response = await communicator.receive_json_from()

            assert response["type"] == "NOTIFICATION"

            data = response["data"]

            assert (
                data["event"]
                == "NOTIFICATION_CREATED"
            )

            assert (
                data["notification"]["message"]
                == "Hello Realtime"
            )

            assert data["unread_count"] == 1

        finally:

            await communicator.disconnect()

    # -------------------------------------

    async def test_notification_read_realtime(
        self,
        user,
        access_token,
    ):

        from notifications.models import Notification

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={access_token}",
        )

        try:

            notification = await sync_to_async(
                Notification.objects.create
            )(
                user=user,
                title="Test",
                message="Hello",
            )

            connected, _ = await communicator.connect()

            assert connected is True

            await sync_to_async(
                NotificationService.mark_as_read
            )(
                user,
                notification.id,
            )

            response = await communicator.receive_json_from()

            assert response["type"] == "NOTIFICATION"

            data = response["data"]

            assert (
                data["event"]
                == "NOTIFICATION_READ"
            )

            assert (
                data["notification_id"]
                == notification.id
            )

            assert data["unread_count"] == 0

        finally:

            await communicator.disconnect()

    # -------------------------------------

    async def test_mark_all_notifications_read_realtime(
        self,
        user,
        access_token,
    ):

        from notifications.models import Notification

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={access_token}",
        )

        try:

            await sync_to_async(
                Notification.objects.create
            )(
                user=user,
                title="1",
                message="1",
            )

            await sync_to_async(
                Notification.objects.create
            )(
                user=user,
                title="2",
                message="2",
            )

            connected, _ = await communicator.connect()

            assert connected is True

            await sync_to_async(
                NotificationService.mark_all_as_read
            )(
                user
            )

            response = await communicator.receive_json_from()

            assert response["type"] == "NOTIFICATION"

            data = response["data"]

            assert (
                data["event"]
                == "NOTIFICATIONS_ALL_READ"
            )

            assert data["unread_count"] == 0

            assert (
                data["has_unread_notifications"]
                is False
            )

        finally:

            await communicator.disconnect()