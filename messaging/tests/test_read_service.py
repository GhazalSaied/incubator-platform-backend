from unittest.mock import patch

import pytest

from messaging.domain.services.read_service import ReadService
from messaging.models import ConversationParticipant


pytestmark = pytest.mark.django_db


class TestReadService:

    def test_mark_as_read_resets_unread(
        self,
        user_factory,
        conversation_factory,
        message_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        message_factory(
            conversation=conversation,
            sender=sender,
            content="hello",
        )

        participant = ConversationParticipant.objects.get(
            conversation=conversation,
            user=receiver,
        )

        participant.unread_count = 5
        participant.save()

        ReadService.mark_conversation_as_read(
            conversation=conversation,
            user=receiver,
        )

        participant.refresh_from_db()

        assert participant.unread_count == 0

    def test_last_read_message_updated(
        self,
        user_factory,
        conversation_factory,
        message_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        message = message_factory(
            conversation=conversation,
            sender=sender,
            content="latest",
        )

        ReadService.mark_conversation_as_read(
            conversation=conversation,
            user=receiver,
        )

        participant = ConversationParticipant.objects.get(
            conversation=conversation,
            user=receiver,
        )

        assert participant.last_read_message == message

    def test_unread_remains_stable_when_already_zero(
        self,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        ReadService.mark_conversation_as_read(
            conversation=conversation,
            user=receiver,
        )

        participant = ConversationParticipant.objects.get(
            conversation=conversation,
            user=receiver,
        )

        assert participant.unread_count == 0

    @patch(
        "messaging.domain.services.read_service.RealtimeService.broadcast_message_read"
    )
    def test_read_broadcast_called(
        self,
        mocked_broadcast,
        user_factory,
        conversation_factory,
        message_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        message_factory(
            conversation=conversation,
            sender=sender,
            content="hello",
        )

        ReadService.mark_conversation_as_read(
            conversation=conversation,
            user=receiver,
        )

        assert mocked_broadcast.called

    def test_read_empty_conversation(
        self,
        user_factory,
        conversation_factory,
    ):
        user = user_factory()
        other = user_factory()

        conversation = conversation_factory(
            participants=[user, other],
        )

        participant = ReadService.mark_conversation_as_read(
            conversation=conversation,
            user=user,
        )

        assert participant.last_read_message is None
        assert participant.unread_count == 0