from messaging.models import Message
from messaging.models import ConversationParticipant
from django.db.models import Sum


# ==========================================
# Conversation Messages
# ==========================================

def get_conversation_messages(conversation):
    return (
        Message.objects
        .select_related("sender")
        .filter(
            conversation=conversation,
            is_deleted=False,
        )
        .order_by("-created_at")
    )


# ==========================================
# Unread Messages Count
# ==========================================

def get_unread_messages_count(
    *,
    conversation,
    user,
):

    participant = (
        conversation.participants
        .select_related("last_read_message")
        .filter(user=user)
        .first()
    )

    if not participant:
        return 0

    queryset = Message.objects.filter(
        conversation=conversation,
        is_deleted=False,
    ).exclude(
        sender=user
    )

    if participant.last_read_message_id:
        queryset = queryset.filter(
            id__gt=participant.last_read_message_id
        )

    return queryset.count()


#=========================================
#GLOBAL Unread Messages Count (BADGE)
#=========================================


def get_global_unread_messages_count(user):

    result = (
        ConversationParticipant.objects
        .filter(user=user)
        .aggregate(total=Sum("unread_count"))
    )

    return result["total"] or 0

# ==========================================
# Latest Message
# ==========================================

def get_latest_conversation_message(conversation):
    return (
        Message.objects
        .filter(
            conversation=conversation,
            is_deleted=False,
        )
        .order_by("-created_at")
        .first()
    )