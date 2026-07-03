from messaging.domain.services.realtime_service import (
    RealtimeService,
)

from messaging.domain.selectors.conversation_selectors import (
    get_conversation_participant_ids,
)

from accounts.models import User

from django.core.cache import cache


class PresenceBroadcastService:


    @classmethod
    def broadcast_to_conversation(
        cls,
        *,
        user_id,
        conversation_id,
        is_online,
    ):
        """
        Send the current presence of one user
        to every other participant in the conversation.
        """

        participant_ids = get_conversation_participant_ids(
            conversation_id
        )

        try:
            user = User.objects.get(
                id=user_id
            )
        except User.DoesNotExist:
            return

        payload = {
            "user_id": user.id,
            "conversation_id": conversation_id,
            "is_online": is_online,
            "last_seen_at": (
                user.last_seen_at.isoformat()
                if user.last_seen_at
                else None
            ),
        }

        for participant_id in participant_ids:

            if participant_id == user.id:
                continue

            RealtimeService.broadcast_presence(
                user_id=participant_id,
                payload=payload,
            )

    @staticmethod
    def _is_online(user_id):
        return bool(
            cache.get(
                f"presence:user:{user_id}:online"
            )
        )

    @classmethod
    def sync_presence_to_user(
        cls,
        *,
        requester_id,
        conversation_id,
    ):
        """
        Send current presence snapshot
        of every other participant
        to one specific user.
        """

        participant_ids = (
            get_conversation_participant_ids(
                conversation_id
            )
        )

        for participant_id in participant_ids:

            if participant_id == requester_id:
                continue

            try:
                user = User.objects.get(
                    id=participant_id
                )

            except User.DoesNotExist:
                continue

            payload = {
                "user_id": user.id,
                "conversation_id": conversation_id,
                "is_online": (
                    cls._is_online(
                        user.id
                    )
                ),
                "last_seen_at": (
                    user.last_seen_at.isoformat()
                    if user.last_seen_at
                    else None
                ),
            }

            RealtimeService.broadcast_presence(
                user_id=requester_id,
                payload=payload,
            )