# messaging/tests/test_message_pagination.py

import pytest

from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User

from messaging.models import (
    Conversation,
    ConversationParticipant,
    Message,
)

from messaging.domain.constants.messaging_constants import (
    ConversationType,
)


@pytest.mark.django_db
def test_messages_pagination_default_page_size():

    user1 = User.objects.create_user(
        email="user1@test.com",
        password="1234",
    )

    user2 = User.objects.create_user(
        email="user2@test.com",
        password="1234",
    )

    conversation = Conversation.objects.create(
        type=ConversationType.PRIVATE,
        created_by=user1,
    )

    ConversationParticipant.objects.create(
        conversation=conversation,
        user=user1,
    )

    ConversationParticipant.objects.create(
        conversation=conversation,
        user=user2,
    )

    # create 25 messages
    for i in range(25):

        Message.objects.create(
            conversation=conversation,
            sender=user1,
            content=f"message {i}",
        )

    client = APIClient()

    client.force_authenticate(user=user1)

    response = client.get(
        f"/api/messaging/conversations/{conversation.id}/messages/"
    )

    assert response.status_code == status.HTTP_200_OK

    # CursorPagination returns "results"
    assert "results" in response.data

    # default page size = 20
    assert len(response.data["results"]) == 20

    # should have next page
    assert response.data["next"] is not None


@pytest.mark.django_db
def test_messages_pagination_custom_page_size():

    user1 = User.objects.create_user(
        email="user1@test.com",
        password="1234",
    )

    user2 = User.objects.create_user(
        email="user2@test.com",
        password="1234",
    )

    conversation = Conversation.objects.create(
        type=ConversationType.PRIVATE,
        created_by=user1,
    )

    ConversationParticipant.objects.create(
        conversation=conversation,
        user=user1,
    )

    ConversationParticipant.objects.create(
        conversation=conversation,
        user=user2,
    )

    # create 15 messages
    for i in range(15):

        Message.objects.create(
            conversation=conversation,
            sender=user1,
            content=f"message {i}",
        )

    client = APIClient()

    client.force_authenticate(user=user1)

    response = client.get(
        f"/api/messaging/conversations/{conversation.id}/messages/?page_size=10"
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data["results"]) == 10


@pytest.mark.django_db
def test_messages_pagination_max_page_size_limit():

    user1 = User.objects.create_user(
        email="user1@test.com",
        password="1234",
    )

    user2 = User.objects.create_user(
        email="user2@test.com",
        password="1234",
    )

    conversation = Conversation.objects.create(
        type=ConversationType.PRIVATE,
        created_by=user1,
    )

    ConversationParticipant.objects.create(
        conversation=conversation,
        user=user1,
    )

    ConversationParticipant.objects.create(
        conversation=conversation,
        user=user2,
    )

    # create 150 messages
    for i in range(150):

        Message.objects.create(
            conversation=conversation,
            sender=user1,
            content=f"message {i}",
        )

    client = APIClient()

    client.force_authenticate(user=user1)

    response = client.get(
        f"/api/messaging/conversations/{conversation.id}/messages/?page_size=500"
    )

    assert response.status_code == status.HTTP_200_OK

    # max_page_size = 100
    assert len(response.data["results"]) == 100


@pytest.mark.django_db
def test_messages_pagination_denied_for_non_participant():

    owner = User.objects.create_user(
        email="owner@test.com",
        password="1234",
    )

    stranger = User.objects.create_user(
        email="stranger@test.com",
        password="1234",
    )

    conversation = Conversation.objects.create(
        type=ConversationType.PRIVATE,
        created_by=owner,
    )

    ConversationParticipant.objects.create(
        conversation=conversation,
        user=owner,
    )

    Message.objects.create(
        conversation=conversation,
        sender=owner,
        content="secret",
    )

    client = APIClient()

    client.force_authenticate(user=stranger)

    response = client.get(
        f"/api/messaging/conversations/{conversation.id}/messages/"
    )

    assert response.status_code in [
        status.HTTP_403_FORBIDDEN,
        status.HTTP_404_NOT_FOUND,
    ]