import pytest
from django.core.cache import cache

from messaging.websocket.services.realtime_presence_service import (
    RealtimePresenceService,
)


pytestmark = pytest.mark.django_db


class TestPresenceService:

    def test_connect_increments_count(
        self,
        user_factory,
    ):
        user = user_factory()

        RealtimePresenceService.connect_user(user.id)

        connections = cache.get(
            RealtimePresenceService.connections_key(
                user.id
            )
        )

        assert connections == 1

    def test_heartbeat_refreshes_ttl(
        self,
        user_factory,
    ):
        user = user_factory()

        RealtimePresenceService.connect_user(user.id)

        RealtimePresenceService.refresh_user_presence(
            user.id
        )

        assert (
            RealtimePresenceService.is_user_online(
                user.id
            )
            is True
        )

    def test_disconnect_decrements_count(
        self,
        user_factory,
    ):
        user = user_factory()

        RealtimePresenceService.connect_user(user.id)
        RealtimePresenceService.connect_user(user.id)

        RealtimePresenceService.disconnect_user(
            user.id
        )

        connections = cache.get(
            RealtimePresenceService.connections_key(
                user.id
            )
        )

        assert connections == 1

    def test_multi_tab_correctness(
        self,
        user_factory,
    ):
        user = user_factory()

        RealtimePresenceService.connect_user(user.id)
        RealtimePresenceService.connect_user(user.id)

        RealtimePresenceService.disconnect_user(
            user.id
        )

        assert (
            RealtimePresenceService.is_user_online(
                user.id
            )
            is True
        )

    def test_disconnect_last_connection_sets_offline(
        self,
        user_factory,
    ):
        user = user_factory()

        RealtimePresenceService.connect_user(user.id)

        RealtimePresenceService.disconnect_user(
            user.id
        )

        assert (
            RealtimePresenceService.is_user_online(
                user.id
            )
            is False
        )

    def test_subscribe_conversation(
        self,
        user_factory,
    ):
        user = user_factory()

        RealtimePresenceService.subscribe_conversation(
            user_id=user.id,
            conversation_id=100,
        )

        assert (
            RealtimePresenceService.is_user_in_conversation(
                user_id=user.id,
                conversation_id=100,
            )
            is True
        )

    def test_unsubscribe_conversation(
        self,
        user_factory,
    ):
        user = user_factory()

        RealtimePresenceService.subscribe_conversation(
            user_id=user.id,
            conversation_id=100,
        )

        RealtimePresenceService.unsubscribe_conversation(
            user_id=user.id,
            conversation_id=100,
        )

        assert (
            RealtimePresenceService.is_user_in_conversation(
                user_id=user.id,
                conversation_id=100,
            )
            is False
        )