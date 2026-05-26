
from rest_framework import serializers

from messaging.models import Message


# ==========================================
# Message Serializer
# ==========================================

class MessageSerializer(serializers.ModelSerializer):

    sender_id = serializers.IntegerField(
        source="sender.id",
        read_only=True,
    )

    sender_name = serializers.CharField(
        source="sender.full_name",
        read_only=True,
    )

    sender_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Message

        fields = [
            "id",
            "conversation",
            "sender_id",
            "sender_name",
            "sender_avatar",
            "content",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "sender_id",
            "sender_name",
            "sender_avatar",
            "created_at",
        ]

    def get_sender_avatar(self, obj):

        if obj.sender.avatar:
            return obj.sender.avatar.url

        return None


# ==========================================
# Send Message Serializer
# ==========================================

class SendMessageSerializer(serializers.Serializer):

    content = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=5000,
    )

    def validate_content(self, value):

        value = value.replace("\x00", "")

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Message content cannot be empty."
            )

        return value


# ==========================================
# Start Conversation Serializer
# ==========================================

class StartConversationSerializer(
    serializers.Serializer
):

    user_id = serializers.IntegerField()

