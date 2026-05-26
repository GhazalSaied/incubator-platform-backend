from django.db.models import Q
from django.db.models import Prefetch

from messaging.models import (
    Conversation,
    ConversationParticipant,
)
from messaging.domain.constants.messaging_constants import ConversationType
from django.db.models import Count


# ==========================================
# Base Conversation Query
# ==========================================

def get_conversation_queryset():
    return (
        Conversation.objects
        .select_related(
            "last_message",
            "last_message__sender",
            "created_by",
        )
        .prefetch_related(
            Prefetch(
                "participants",
                queryset=(
                    ConversationParticipant.objects
                    .select_related(
                        "user",
                        "last_read_message",
                    )
                )
            )
        )
    )


# ==========================================
# User Conversations
# ==========================================

def get_user_conversations(user, search=None):

    queryset = (
        get_conversation_queryset()
        .filter(participants__user=user)
        .distinct()
    )

    if search:

        queryset = queryset.filter(
            participants__user__full_name__icontains=search,
        ).exclude(
            participants__user=user, 
        ).distinct()
    

    return queryset.order_by(
        "-last_message_at",
        "-created_at",
    )


# ==========================================
# Single Conversation
# ==========================================

def get_user_conversation_by_id(
    *,
    user,
    conversation_id,
):
    return (
        get_conversation_queryset()
        .filter(
            id=conversation_id,
            participants__user=user,
        )
        .first()
    )


# ==========================================
# Existing Private Conversation
# ==========================================

def get_private_conversation_between_users(
    *,
    user_1,
    user_2,
):
    return (
        get_conversation_queryset()
        .filter(
            type=ConversationType.PRIVATE,
            participants__user=user_1,
        )
        .filter(
            participants__user=user_2,
        )
        .annotate(
            participants_count=Count("participants")
        )
        .filter(
            participants_count=2
        )
        .distinct()
        .first()
    )


# ==========================================
# Conversation Participant
# ==========================================

def get_conversation_participant(
    *,
    conversation,
    user,
):
    return (
        ConversationParticipant.objects
        .select_related(
            "user",
            "conversation",
            "last_read_message",
        )
        .filter(
            conversation=conversation,
            user=user,
        )
        .first()
    )