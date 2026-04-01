from rest_framework import serializers
from bootcamp.models import BootcampSession


class BootcampSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = BootcampSession
        fields = [
            "id",
            "title",
            "trainer_name",
            "location",
            "tasks",
            "date",
            "start_time",
            "end_time",
            "status"
        ]

    def get_trainer_name(self, obj):
        return obj.trainer.username if obj.trainer else None

    def get_status(self, obj):
        return "active" if obj.is_active else "inactive"