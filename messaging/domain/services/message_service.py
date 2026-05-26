
from django.db import transaction
from django.utils import timezone
from django.db.models import F

from messaging.models import Message

from messaging.domain.exceptions.messaging_exceptions import (
    EmptyMessageContent,
)

from messaging.domain.services.realtime_service import (
    RealtimeService,
)

from messaging.api.serializers.message_serializers import (
    MessageSerializer,
)

from messaging.models import (
    ConversationParticipant,
    Conversation
)

from notifications.services.notification_service import (
    NotificationService,
)

from messaging.websocket.services.realtime_presence_service import (
    RealtimePresenceService,
)



from core.events import EventBus


class MessageService:

    @staticmethod
    @transaction.atomic
    def send_message(
        *,
        conversation,
        sender,
        content,
    ):

        content = content.strip()

        if not content:
            raise EmptyMessageContent()

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content,
        )

        Conversation.objects.filter(
            id=conversation.id
        ).update(
            last_message=message,
            last_message_at=message.created_at,
        )

        sender_participant = (
            ConversationParticipant.objects
            .select_for_update()
            .filter(
                conversation=conversation,
                user=sender,
            )
            .first()
        )

        if sender_participant:
            sender_participant.unread_count = 0
            sender_participant.last_read_message = message
            sender_participant.last_read_at = timezone.now()

            sender_participant.save(
                update_fields=[
                    "unread_count",
                    "last_read_message",
                    "last_read_at",
                    "updated_at",
                ]
            )

        (
            ConversationParticipant.objects
            .filter(conversation=conversation)
            .exclude(user=sender)
            .update(unread_count=F("unread_count") + 1)
        )


        def emit_message_sent_event():


            # =================================
            # REALTIME MESSAGE
            # =================================

            RealtimeService.broadcast_new_message(
                conversation_id=conversation.id,
                payload=MessageSerializer(
                    message
                ).data,
            )


        transaction.on_commit(
            emit_message_sent_event
        )

        return message
    


    @staticmethod
    def should_send_notification(
        *,
        receiver,
        conversation,
    ):

        # المستخدم offline
        if not (
            RealtimePresenceService
            .is_user_online(receiver.id)
        ):
            return True

        # المستخدم ليس داخل نفس المحادثة
        in_conversation = (
            RealtimePresenceService
            .is_user_in_conversation(
                user_id=receiver.id,
                conversation_id=conversation.id,
            )
        )

        return not in_conversation

