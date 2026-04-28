from rest_framework import serializers
from .models import Conversation, Message
from django.db.models import Count, Q



# /////////////////////// Display Participants  //////////////////////

class ParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    avatar = serializers.CharField(allow_null=True)


#///////////////////////////// MESSAGE /////////////////////////

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


#/////////////////////////// CONVERSATION //////////////////////////////

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
                "email": user.email,
                "full_name": user.full_name,
                "avatar": user.avatar.url if user.avatar else None
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

#////////////////////////////// CONVERSATION LIST //////////////////////////

class ConversationListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "other_user",
            "last_message",
            "unread_count",
            "created_at",
        ]

    def get_other_user(self, obj):
        request = self.context.get("request")
        user = request.user

        other = obj.participants.exclude(id=user.id).first()

        if not other:
            return None

        return {
            "id": other.id,
            "email": other.email,
            "full_name": other.full_name,
            "avatar": other.avatar.url if other.avatar else None
        }

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        if not last:
            return None

        return {
            "content": last.content,
            "sender": last.sender.email,
            "created_at": last.created_at,
        }

    def get_unread_count(self, obj):
        request = self.context.get("request")

        return obj.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()
    
    
    def get_participants(self, obj):
        return [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "avatar": u.avatar.url if u.avatar else None
            }
            for u in obj.participants.all()
        ]