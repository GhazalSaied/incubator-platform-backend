import pytest

from messaging.models import ConversationParticipant


pytestmark = pytest.mark.django_db


class TestMessageAPI:

    def test_cursor_pagination(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
        message_factory,
    ):
        user = user_factory()
        other = user_factory()

        conversation = conversation_factory(
            participants=[user, other],
        )

        for index in range(30):
            message_factory(
                conversation=conversation,
                sender=user,
                content=f"message-{index}",
            )

        client = authenticated_client(user)

        response = client.get(
            f"/api/messaging/conversations/{conversation.id}/messages/"
        )

        assert response.status_code == 200
        assert len(response.data["results"]) == 20
        assert response.data["next"] is not None

    def test_read_endpoint(
        self,
        authenticated_client,
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

        client = authenticated_client(receiver)

        response = client.post(
            f"/api/messaging/conversations/{conversation.id}/read/"
        )

        participant.refresh_from_db()

        assert response.status_code == 200
        assert participant.unread_count == 0

    def test_unauthorized_access(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
    ):
        owner = user_factory()
        other = user_factory()
        intruder = user_factory()

        conversation = conversation_factory(
            participants=[owner, other],
        )

        client = authenticated_client(intruder)

        response = client.get(
            f"/api/messaging/conversations/{conversation.id}/messages/"
        )

        assert response.status_code == 403

    def test_send_message_behavior(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        client = authenticated_client(sender)

        response = client.post(
            f"/api/messaging/conversations/{conversation.id}/messages/send/",
            {
                "content": "hello world",
            },
            format="json",
        )

        assert response.status_code == 201
        assert response.data["content"] == "hello world"

    def test_blank_message_rejected(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
    ):
        sender = user_factory()
        receiver = user_factory()

        conversation = conversation_factory(
            participants=[sender, receiver],
        )

        client = authenticated_client(sender)

        response = client.post(
            f"/api/messaging/conversations/{conversation.id}/messages/send/",
            {
                "content": "    ",
            },
            format="json",
        )

        assert response.status_code == 400

    def test_global_unread_count(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
    ):
        user = user_factory()
        other = user_factory()

        conversation = conversation_factory(
            participants=[user, other],
        )

        participant = ConversationParticipant.objects.get(
            conversation=conversation,
            user=user,
        )

        participant.unread_count = 9
        participant.save()

        client = authenticated_client(user)

        response = client.get(
            "/api/messaging/messages/unread-count/"
        )

        assert response.status_code == 200
        assert response.data["unread_count"] == 9