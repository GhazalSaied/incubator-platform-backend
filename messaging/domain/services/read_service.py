
from django.db import transaction
from django.utils import timezone

from messaging.models import (Message,ConversationParticipant)

from messaging.domain.services.realtime_service import (
    RealtimeService,
)


from django.db import transaction
from django.utils import timezone


class ReadService:

    @staticmethod
    @transaction.atomic
    def mark_conversation_as_read(
        *,
        conversation,
        user,
    ):

        participant = (
            ConversationParticipant.objects
            .select_for_update()
            .filter(
                conversation=conversation,
                user=user,
            )
            .first()
        )

        if not participant:
            return None

        latest_message = (
            Message.objects
            .filter(
                conversation=conversation,
                is_deleted=False,
            )
            .order_by("-created_at")
            .first()
        )

        participant.last_read_message = latest_message
        participant.last_read_at = timezone.now()
        participant.unread_count = 0

        participant.save(
            update_fields=[
                "last_read_message",
                "last_read_at",
                "unread_count",
                "updated_at",
            ]
        )

        def emit_read_events():

            RealtimeService.broadcast_conversation_updated(
                user_id=user.id,
                payload={
                    "conversation_id": conversation.id,
                    "unread_count": 0,
                    "last_message_at": (
                        conversation.last_message_at.isoformat()
                        if conversation.last_message_at
                        else None
                    ),
                },
            )

            if latest_message:

                RealtimeService.broadcast_message_read(
                    conversation_id=conversation.id,
                    payload={
                        "conversation_id": conversation.id,
                        "user_id": user.id,
                        "message_id": latest_message.id,
                        "read_at": participant.last_read_at.isoformat(),
                    },
                )

        transaction.on_commit(
            emit_read_events
        )

        return participant