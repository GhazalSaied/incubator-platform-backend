import uuid

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from messaging.models import (
    Conversation,
    ConversationParticipant,
    Message,
)
from messaging.domain.constants.messaging_constants import (
    ConversationType,
)


User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    def factory(**kwargs):
        unique = uuid.uuid4().hex[:8]

        defaults = {
            "email": f"user_{unique}@test.com",
            "full_name": f"User {unique}",
            "password": "StrongPassword123",
        }

        defaults.update(kwargs)

        password = defaults.pop("password")

        user = User.objects.create_user(
            password=password,
            **defaults,
        )

        return user

    return factory


@pytest.fixture
def authenticated_client(api_client):
    def factory(user):
        refresh = RefreshToken.for_user(user)

        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        return api_client

    return factory


@pytest.fixture
def conversation_factory(db):
    def factory(
        *,
        participants=None,
        conversation_type=ConversationType.PRIVATE,
        created_by=None,
    ):
        conversation = Conversation.objects.create(
            type=conversation_type,
            created_by=created_by,
        )

        participants = participants or []

        for user in participants:
            ConversationParticipant.objects.create(
                conversation=conversation,
                user=user,
            )

        return conversation

    return factory


@pytest.fixture
def participant_factory(db):
    def factory(**kwargs):
        return ConversationParticipant.objects.create(**kwargs)

    return factory


@pytest.fixture
def message_factory(db):
    def factory(**kwargs):
        return Message.objects.create(**kwargs)

    return factory