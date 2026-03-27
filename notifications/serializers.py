from rest_framework import serializers
from .models import Notification

#/////////////////////////// NOTIFICATIONS /////////////////////////

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "type",
            "action_url",
            "is_read",
            "created_at",
        ]