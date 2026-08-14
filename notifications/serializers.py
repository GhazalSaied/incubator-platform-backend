from rest_framework import serializers
from django.utils.timesince import timesince

from django.utils.timezone import localtime, now
from .models import Notification


#/////////////////////////// NOTIFICATIONS /////////////////////////

class NotificationSerializer(serializers.ModelSerializer):
    time_since = serializers.SerializerMethodField()
    formatted_created_at = serializers.SerializerMethodField()
    has_action = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "message",
            "type",
            "has_action",
            "action_url",
            "target_role",
            "is_read",
            "formatted_created_at",
            "time_since",
        ]

    def get_time_since(self, obj):
       return timesince(obj.created_at, now())
    
    
    def get_formatted_created_at(self, obj):
        local_date = localtime(obj.created_at)

        return local_date.strftime("%A %I:%M %p")
    

    def get_has_action(self, obj):

        return bool(obj.action_url)
    

    def to_representation(self, instance):
        data = super().to_representation(instance)

 

        return data