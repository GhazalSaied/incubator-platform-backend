from rest_framework import serializers

from messaging.domain.constants.contact_constants import (
    ContactInquiryType,
)


class ContactUsSerializer(serializers.Serializer):

    type = serializers.ChoiceField(
        choices=ContactInquiryType.CHOICES
    )

    message = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=5000,
    )

    def validate_message(self, value):

        value = value.replace("\x00", "").strip()

        if not value:
            raise serializers.ValidationError(
                "Message cannot be empty."
            )

        return value