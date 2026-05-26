import pytest

from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken

from core.asgi import application


pytestmark = pytest.mark.asyncio


@pytest.mark.django_db(transaction=True)
class TestRealtimeConsumer:

    async def test_websocket_auth_success(
        self,
        user_factory,
    ):
        user = await sync_to_async(user_factory)()

        token = str(
            RefreshToken.for_user(user).access_token
        )

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={token}",
        )

        connected, _ = await communicator.connect()

        assert connected is True

        await communicator.disconnect()

    async def test_websocket_auth_failure(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/realtime/?token=invalid",
        )

        connected, _ = await communicator.connect()

        assert connected is False

    async def test_heartbeat_ack(
        self,
        user_factory,
    ):
        user = await sync_to_async(user_factory)()

        token = str(
            RefreshToken.for_user(user).access_token
        )

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={token}",
        )

        connected, _ = await communicator.connect()

        assert connected is True

        await communicator.send_json_to({
            "type": "HEARTBEAT",
        })

        response = await communicator.receive_json_from()

        assert response["type"] == "HEARTBEAT_ACK"

        await communicator.disconnect()

    async def test_subscribe_conversation(
        self,
        user_factory,
        conversation_factory,
    ):
        user = await sync_to_async(user_factory)()

        other = await sync_to_async(user_factory)()

        conversation = await sync_to_async(
            conversation_factory
        )(
            participants=[user, other],
        )

        token = str(
            RefreshToken.for_user(user).access_token
        )

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={token}",
        )

        connected, _ = await communicator.connect()

        assert connected is True

        await communicator.send_json_to({
            "type": "SUBSCRIBE_CONVERSATION",
            "conversation_id": conversation.id,
        })

        response = await communicator.receive_json_from()

        assert response["type"] == "SUBSCRIBED"

        await communicator.disconnect()

    async def test_access_denied_subscription(
        self,
        user_factory,
        conversation_factory,
    ):
        owner = await sync_to_async(user_factory)()

        other = await sync_to_async(user_factory)()

        intruder = await sync_to_async(user_factory)()

        conversation = await sync_to_async(
            conversation_factory
        )(
            participants=[owner, other],
        )

        token = str(
            RefreshToken.for_user(intruder).access_token
        )

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={token}",
        )

        connected, _ = await communicator.connect()

        assert connected is True

        await communicator.send_json_to({
            "type": "SUBSCRIBE_CONVERSATION",
            "conversation_id": conversation.id,
        })

        response = await communicator.receive_json_from()

        assert response["code"] == "CONVERSATION_ACCESS_DENIED"

        await communicator.disconnect()