from rest_framework import serializers
from django.utils.timesince import timesince
from django.utils.timezone import now

from .models import Notification


#/////////////////////////// NOTIFICATIONS /////////////////////////

class NotificationSerializer(serializers.ModelSerializer):
    time_since = serializers.SerializerMethodField()

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
            "time_since",
        ]

    def get_time_since(self, obj):
        return timesince(obj.created_at, now()) + " ago"