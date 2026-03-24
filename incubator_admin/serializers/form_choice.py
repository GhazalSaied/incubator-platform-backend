from rest_framework import serializers
from ideas.models import FormQuestionChoice, FormQuestion


class FormQuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormQuestionChoice
        fields = ['id', 'value', 'label', 'order']

