from rest_framework import serializers
from .models import Conversation, Message


# Display Participants
class ParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()


# Message
class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source="sender.email", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "sender_email",
            "content",
            "created_at",
            "is_read"
        ]
        read_only_fields = ["sender", "created_at", "is_read"]


# conversation
class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "created_at",
            "last_message"
        ]

    def get_participants(self, obj):
        return [
            {
                "id": user.id,
                "email": user.email
            }
            for user in obj.participants.all()
        ]

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        if not last:
            return None
        return {
            "content": last.content,
            "sender": last.sender.email,
            "created_at": last.created_at
        }