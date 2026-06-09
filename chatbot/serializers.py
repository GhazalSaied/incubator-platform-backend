from rest_framework import serializers
from volunteers.models import PrimarySkillChoices


class SendMessageSerializer(serializers.Serializer):

    session_id = serializers.IntegerField(
        required=False,allow_null=True
    )

    consultation_field = serializers.ChoiceField(
        choices=PrimarySkillChoices.choices,
        required=False
    )

    message = serializers.CharField()