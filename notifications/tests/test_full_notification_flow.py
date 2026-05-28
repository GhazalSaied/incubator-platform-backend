import pytest

from asgiref.sync import sync_to_async

from channels.testing import (
    WebsocketCommunicator,
)

from core.asgi import application

from core.events import EventBus

from notifications.models import (
    Notification,
)

from accounts.models import User


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestFullNotificationFlow:

    async def test_full_notification_flow_workshop_submitted(
        self,
        access_token,
    ):

        # =====================================
        # CREATE ADMIN USER
        # =====================================

        admin = await sync_to_async(
            User.objects.create_user
        )(
            email="admin@test.com",
            password="12345678",
            is_staff=True,
        )

        admin_access_token = access_token

        # =====================================
        # CONNECT WEBSOCKET
        # =====================================

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={admin_access_token}",
        )

        try:

            connected, _ = await communicator.connect()

            assert connected is True

            # =================================
            # FAKE WORKSHOP OBJECT
            # =================================

            class FakeWorkshop:
                id = 1
                title = "Realtime Workshop"

            class FakeActor:
                full_name = "Test User"

            workshop = FakeWorkshop()
            actor = FakeActor()

            # =================================
            # EMIT EVENT
            # =================================

            await sync_to_async(
                EventBus.emit
            )(
                "workshop_submitted",
                workshop=workshop,
                actor=actor,
            )

            # =================================
            # RECEIVE REALTIME EVENT
            # =================================

            response = await communicator.receive_json_from()

            assert response["type"] == "NOTIFICATION"

            data = response["data"]

            # =================================
            # ASSERT EVENT TYPE
            # =================================

            assert (
                data["event"]
                == "NOTIFICATION_CREATED"
            )

            # =================================
            # ASSERT NOTIFICATION DATA
            # =================================

            notification = data["notification"]

            assert (
                notification["message"]
                == (
                    "تمت إضافة ورشة جديدة بعنوان "
                    "Realtime Workshop "
                    "من قبل Test User"
                )
            )

            assert notification["is_read"] is False

            assert data["unread_count"] == 1

            assert (
                data["has_unread_notifications"]
                is True
            )

            # =================================
            # ASSERT DATABASE RECORD CREATED
            # =================================

            exists = await sync_to_async(
                Notification.objects.filter(
                    user=admin,
                    title="ورشة جديدة",
                ).exists
            )()

            assert exists is True

        finally:

            await communicator.disconnect()