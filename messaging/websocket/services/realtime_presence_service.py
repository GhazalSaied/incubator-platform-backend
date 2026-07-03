from django.core.cache import cache
from django.utils import timezone

from accounts.models import User

from messaging.websocket.services.presence_broadcast_service import (
    PresenceBroadcastService,
)

from messaging.models import ConversationParticipant


class RealtimePresenceService:

    ONLINE_TTL = 70

    @classmethod
    def online_key(cls, user_id):
        return f"presence:user:{user_id}:online"
    
    @classmethod
    def connections_key(cls, user_id):
        return f"presence:user:{user_id}:connections"

    @classmethod
    def conversations_key(cls, user_id):
        return (
            f"presence:user:{user_id}:conversations"
        )
    

    # ==========================================
    # Presence Broadcast
    # ==========================================
    
    @classmethod
    def _broadcast_presence_to_active_conversations(
        cls,
        user_id,
        is_online,
    ):
        """
        Broadcast the user's latest presence
        to every conversation he participates in.
        """

        conversation_ids = (
            ConversationParticipant.objects.filter(
                user_id=user_id,
            )
            .values_list(
                "conversation_id",
                flat=True,
            )
            .distinct()
        )

        for conversation_id in conversation_ids:

            PresenceBroadcastService.broadcast_to_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                is_online=is_online,
            )
    


    # =====================================
    # ONLINE STATUS
    # =====================================

    @classmethod
    def connect_user(cls, user_id):

        connections_key = cls.connections_key(user_id)

        connections = cache.get(connections_key, 0)

        cache.set(
            connections_key,
            connections + 1,
            timeout=cls.ONLINE_TTL * 2,
        )

        cache.set(
            cls.online_key(user_id),
            True,
            timeout=cls.ONLINE_TTL,
        )

        cls._broadcast_presence_to_active_conversations(
            user_id=user_id,
            is_online=True,
        )

    @classmethod
    def refresh_user_presence(cls, user_id):

        cache.set(
            cls.online_key(user_id),
            True,
            timeout=cls.ONLINE_TTL,
        )

        conversations = cache.get(
            cls.conversations_key(user_id)
        )

        if conversations is not None:
            cache.set(
                cls.conversations_key(user_id),
                conversations,
                timeout=cls.ONLINE_TTL,
            )

    @classmethod
    def disconnect_user(cls, user_id):

        connections_key = cls.connections_key(user_id)

        connections = cache.get(connections_key, 0)

        connections = max(connections - 1, 0)

        if connections > 0:

            cache.set(
                connections_key,
                connections,
                timeout=cls.ONLINE_TTL * 2,
            )

            return

        cache.delete(connections_key)

        cache.delete(
            cls.online_key(user_id)
        )

        cache.delete(
            cls.conversations_key(user_id)
        )

        User.objects.filter(
            id=user_id
        ).update(
            last_seen_at=timezone.now()
        )

        cls._broadcast_presence_to_active_conversations(
            user_id=user_id,
            is_online=False,
        )

    @classmethod
    def is_user_online(cls, user_id):

        return bool(
            cache.get(
                cls.online_key(user_id)
            )
        )

    # =====================================
    # CONVERSATIONS
    # =====================================

    @classmethod
    def subscribe_conversation(
        cls,
        *,
        user_id,
        conversation_id,
    ):

        key = cls.conversations_key(
            user_id
        )

        conversations = cache.get(
            key,
            [],
        )

        conversation_id = str(conversation_id)

        if conversation_id not in conversations:
            conversations.append(conversation_id)

        cache.set(
            key,
            conversations,
            timeout=cls.ONLINE_TTL,
        )

    @classmethod
    def unsubscribe_conversation(
        cls,
        *,
        user_id,
        conversation_id,
    ):

        key = cls.conversations_key(
            user_id
        )

        conversations = cache.get(
            key,
            [],
        )

        conversation_id = str(conversation_id)

        if conversation_id in conversations:
            conversations.remove(conversation_id)

        cache.set(
            key,
            conversations,
            timeout=cls.ONLINE_TTL,
        )

    @classmethod
    def get_conversation_active_users(
        cls,
        conversation_id,
    ):

        active_users = []

        for user in User.objects.all():

            conversations = cache.get(
                cls.conversations_key(user.id),
                [],
            )

            if str(conversation_id) in conversations:

                active_users.append(user.id)

        return active_users

    @classmethod
    def is_user_in_conversation(
        cls,
        *,
        user_id,
        conversation_id,
    ):

        conversations = cache.get(
            cls.conversations_key(user_id),
            [],
        )

        print(
            "CACHE CHECK",
            "USER=", user_id,
            "CONVERSATIONS=", conversations,
            "LOOKING_FOR=", conversation_id,
        )

        return (
            str(conversation_id)
            in conversations
        )