
from rest_framework import serializers

from messaging.models import (
    Conversation,
    ConversationParticipant,
)
from messaging.websocket.services.realtime_presence_service import (
        RealtimePresenceService,
    )


# ==========================================
# User Preview Serializer
# ==========================================

class ConversationUserSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    email = serializers.EmailField()

    full_name = serializers.CharField()

    avatar = serializers.SerializerMethodField()

    is_online = serializers.SerializerMethodField()

    last_seen_at = serializers.DateTimeField(
        read_only=True,
    )


    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None
    

    def get_is_online(self, obj):

        return (
            RealtimePresenceService
            .is_user_online(obj.id)
        )

# ==========================================
# Last Message Serializer
# ==========================================

class LastMessageSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    content = serializers.CharField()

    created_at = serializers.DateTimeField()

    sender_id = serializers.IntegerField(
        source="sender.id"
    )

    sender_name = serializers.CharField(
        source="sender.full_name"
    )


# ==========================================
# Conversation List Serializer
# ==========================================

def _get_other_participant(conversation, current_user_id):

    participants = getattr(
        conversation,
        "prefetched_participants",
        None,
    )

    if participants is None:
        participants = conversation.participants.all()

    for participant in participants:
        if participant.user_id != current_user_id:
            return participant

    return None

class ConversationListSerializer(
    serializers.ModelSerializer
):
    
    
    

    other_user = serializers.SerializerMethodField()

    last_message = serializers.SerializerMethodField()

    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation

        fields = [
            "id",
            "type",
            "title",
            "avatar",
            "last_message",
            "last_message_at",
            "other_user",
            "unread_count",
        ]

    def get_other_user(self, obj):

        request = self.context["request"]

        participant = _get_other_participant(
            obj,
            request.user.id,
        )

        if not participant:
            return None

        return ConversationUserSerializer(
            participant.user
        ).data

    def get_last_message(self, obj):

        if not obj.last_message:
            return None

        return LastMessageSerializer(
            obj.last_message
        ).data

    def get_unread_count(self, obj):

        request = self.context["request"]

        participants = getattr(
            obj,
            "prefetched_participants",
            None,
        )

        if participants is None:
            participants = obj.participants.all()

        for participant in participants:
            if participant.user_id == request.user.id:
                return participant.unread_count

        return 0
    



# ==========================================
# Conversation Detail Serializer
# ==========================================

class ConversationDetailSerializer(
    serializers.ModelSerializer
):

    participants = serializers.SerializerMethodField()

    class Meta:
        model = Conversation

        fields = [
            "id",
            "type",
            "title",
            "avatar",
            "participants",
            "last_message_at",
            "created_at",
        ]

    def get_participants(self, obj):

        participants = (
            obj.participants
            .select_related("user")
            .all()
        )

        return [
            ConversationUserSerializer(
                participant.user
            ).data
            for participant in participants
        ]

