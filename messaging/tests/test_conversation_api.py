import pytest
from django.urls import reverse
from django.utils import timezone

from messaging.models import ConversationParticipant


pytestmark = pytest.mark.django_db


class TestConversationAPI:

    def test_conversation_ordering(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
        message_factory,
    ):
        user = user_factory()
        other_1 = user_factory(full_name="Ahmed")
        other_2 = user_factory(full_name="Mohamed")

        older = conversation_factory(
            participants=[user, other_1],
        )

        newer = conversation_factory(
            participants=[user, other_2],
        )

        old_message = message_factory(
            conversation=older,
            sender=user,
            content="old",
        )

        new_message = message_factory(
            conversation=newer,
            sender=user,
            content="new",
        )

        older.last_message = old_message
        older.last_message_at = old_message.created_at
        older.save()

        newer.last_message = new_message
        newer.last_message_at = timezone.now()
        newer.save()

        client = authenticated_client(user)

        response = client.get("/api/messaging/conversations/")

        assert response.status_code == 200
        assert response.data[0]["id"] == newer.id

    def test_unread_values(
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

        participant.unread_count = 4
        participant.save()

        client = authenticated_client(user)

        response = client.get("/api/messaging/conversations/")

        assert response.status_code == 200
        assert response.data[0]["unread_count"] == 4

    def test_search_behavior(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
    ):
        user = user_factory()

        ahmed = user_factory(full_name="Ahmed Ali")
        sara = user_factory(full_name="Sara Ali")

        conversation_factory(participants=[user, ahmed])
        conversation_factory(participants=[user, sara])

        client = authenticated_client(user)

        response = client.get(
            "/api/messaging/conversations/?search=Ahmed"
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert (
            response.data[0]["other_user"]["full_name"]
            == "Ahmed Ali"
        )

    def test_access_control_requires_authentication(
        self,
        api_client,
    ):
        response = api_client.get(
            "/api/messaging/conversations/"
        )

        assert response.status_code == 401

    def test_conversation_detail_access_denied(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
    ):
        owner = user_factory()
        intruder = user_factory()
        other = user_factory()

        conversation = conversation_factory(
            participants=[owner, other],
        )

        client = authenticated_client(intruder)

        response = client.get(
            f"/api/messaging/conversations/{conversation.id}/"
        )

        assert response.status_code == 403

    def test_search_excludes_current_user_name(
        self,
        authenticated_client,
        user_factory,
        conversation_factory,
    ):
        current_user = user_factory(full_name="Current User")
        other = user_factory(full_name="Another User")

        conversation_factory(
            participants=[current_user, other],
        )

        client = authenticated_client(current_user)

        response = client.get(
            "/api/messaging/conversations/?search=Current"
        )

        assert response.status_code == 200
        assert len(response.data) == 0