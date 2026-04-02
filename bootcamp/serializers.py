from rest_framework import serializers
from .models import BootcampSession


#/////////////////////////// BOOTCAMP SESSION ////////////////////////

class BootcampSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source="trainer.full_name", read_only=True)

    class Meta:
        model = BootcampSession
        fields = [
            "id",
            "title",
            "trainer_name",
            "location",
            "start_time",
            "end_time",
        ]