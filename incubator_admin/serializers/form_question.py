from rest_framework import serializers
from ideas.models import FormQuestion, IdeaForm


class FormQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormQuestion
        fields = [
            'id',
            'form',
            'key',
            'label',
            'type',
            'required',
            'order',
        ]
        read_only_fields = ['form']

    def validate_key(self, value):
        if ' ' in value:
            raise serializers.ValidationError(
                "key لا يجب أن يحتوي على مسافات"
            )
        return value
