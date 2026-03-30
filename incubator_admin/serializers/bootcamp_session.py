from rest_framework import serializers
from bootcamp.models import BootcampSession


class BootcampSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = BootcampSession
        fields = "__all__"