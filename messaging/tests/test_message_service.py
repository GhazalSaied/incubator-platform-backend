from unittest.mock import patch

import pytest
from django.utils import timezone

from messaging.domain.exceptions.messaging_exceptions import (
    EmptyMessageContent,
)
from messaging.domain.services.message_service import (
    MessageService,
)
from messaging.models import (
    ConversationParticipant,
    Message,
)


pytestmark = pytest.mark.django_db(transaction=True)


class TestMessageService:

    def test_send_message_increments_receiver_unread(
        self,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
            created_by=sender,
        )

        MessageService.send_message(
            conversation=conversation,
            sender=sender,
            content="hello",
        )

        receiver_participant = (
            ConversationParticipant.objects.get(
                conversation=conversation,
                user=receiver,
            )
        )

        assert receiver_participant.unread_count == 1

    def test_sender_unread_reset_after_send(
        self,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        sender_participant = (
            ConversationParticipant.objects.get(
                conversation=conversation,
                user=sender,
            )
        )

        sender_participant.unread_count = 10
        sender_participant.save()

        message = MessageService.send_message(
            conversation=conversation,
            sender=sender,
            content="test",
        )

        sender_participant.refresh_from_db()

        assert sender_participant.unread_count == 0
        assert sender_participant.last_read_message == message
        assert sender_participant.last_read_at is not None

    def test_conversation_last_message_updated(
        self,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        message = MessageService.send_message(
            conversation=conversation,
            sender=sender,
            content="latest",
        )

        conversation.refresh_from_db()

        assert conversation.last_message == message
        assert conversation.last_message_at is not None

    def test_empty_message_validation(
        self,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        with pytest.raises(EmptyMessageContent):
            MessageService.send_message(
                conversation=conversation,
                sender=sender,
                content="    ",
            )

    def test_message_content_trimmed(
        self,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        message = MessageService.send_message(
            conversation=conversation,
            sender=sender,
            content="   hello world   ",
        )

        assert message.content == "hello world"

    @patch(
        "messaging.domain.services.message_service.RealtimeService.broadcast_new_message"
    )

    def test_emit_and_broadcast_called(
        self,
        
        mocked_broadcast,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        MessageService.send_message(
            conversation=conversation,
            sender=sender,
            content="hello",
        )

       
        assert mocked_broadcast.called

    def test_message_created_in_database(
        self,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        MessageService.send_message(
            conversation=conversation,
            sender=sender,
            content="persist",
        )

        assert Message.objects.count() == 1

    def test_last_message_at_updated_after_send(
        self,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        before = timezone.now()

        MessageService.send_message(
            conversation=conversation,
            sender=sender,
            content="timestamp",
        )

        conversation.refresh_from_db()

        assert conversation.last_message_at >= before