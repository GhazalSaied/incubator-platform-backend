import pytest

from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken

from core.asgi import application
from messaging.models import ConversationParticipant


pytestmark = pytest.mark.asyncio


@pytest.mark.django_db(transaction=True)
class TestMessagingIntegrationFlow:

    async def test_complete_user_messaging_flow(
        self,
        user_factory,
        conversation_factory,
    ):
        user_a = await sync_to_async(user_factory)(
            full_name="User A",
        )

        user_b = await sync_to_async(user_factory)(
            full_name="User B",
        )

        conversation = await sync_to_async(
            conversation_factory
        )(
            participants=[user_a, user_b],
            created_by=user_a,
        )

        token_b = str(
            RefreshToken.for_user(user_b).access_token
        )

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={token_b}",
        )

        connected, _ = await communicator.connect()

        assert connected is True

        await communicator.send_json_to({
            "type": "SUBSCRIBE_CONVERSATION",
            "conversation_id": conversation.id,
        })

        await communicator.receive_json_from()

        from messaging.domain.services.message_service import (
            MessageService,
        )

        message = await sync_to_async(
            MessageService.send_message
        )(
            conversation=conversation,
            sender=user_a,
            content="hello realtime",
        )

        realtime_payload = (
            await communicator.receive_json_from()
        )

        assert realtime_payload["type"] == "NEW_MESSAGE"

        assert (
            realtime_payload["data"]["content"]
            == "hello realtime"
        )

        participant = await sync_to_async(
            ConversationParticipant.objects.get
        )(
            conversation=conversation,
            user=user_b,
        )

        assert participant.unread_count == 1

        await communicator.disconnect()