from rest_framework import serializers


class AdminBroadcastSerializer(serializers.Serializer):

    TARGET_CHOICES = [
        ("ALL", "All Users"),

        ("VOLUNTEERS", "Volunteers"),

        ("EVALUATORS", "Evaluators"),

        ("INCUBATORS", "Incubators"),

        ("IDEA_OWNERS", "Idea Owners"),
    ]

    target = serializers.ChoiceField(
        choices=TARGET_CHOICES
    )

    message = serializers.CharField(
        max_length=2000
    )