
from django.db import transaction
from django.core.exceptions import ValidationError

from messaging.models import (
    Conversation,
    ConversationParticipant,
)

from messaging.domain.constants.messaging_constants import (
    ConversationType,
)

from messaging.domain.selectors.conversation_selectors import (
    get_private_conversation_between_users,
)

from messaging.domain.exceptions.messaging_exceptions import (
    ConversationAlreadyExists,
)


class ConversationService:

    @staticmethod
    @transaction.atomic
    def start_private_conversation(
        *,
        creator,
        target_user,
    ):
        """
        Create private conversation between two users.
        """

        if creator.id == target_user.id:
            raise ValidationError(
                "Cannot create conversation with yourself."
            )
        
        user_ids = sorted([
            creator.id,
            target_user.id,
        ])

        participants = (
            ConversationParticipant.objects
            .select_for_update()
            .filter(user_id__in=user_ids)
        )
        
        existing_conversation = (
            get_private_conversation_between_users(
                user_1=creator,
                user_2=target_user,
            )
        )

        if existing_conversation:
            return existing_conversation

        conversation = Conversation.objects.create(
            type=ConversationType.PRIVATE,
            created_by=creator,
        )

        ConversationParticipant.objects.bulk_create([
            ConversationParticipant(
                conversation=conversation,
                user=creator,
            ),
            ConversationParticipant(
                conversation=conversation,
                user=target_user,
            ),
        ])

        return conversation

