from rest_framework import serializers
from .models import Idea, FormQuestion, IdeaForm, Season

#///////////////////////////IDAE FORM SERIALIZER /////////////////////////////////


class FormQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormQuestion
        fields = ['key', 'label', 'type', 'required', 'order']


class IdeaFormSerializer(serializers.ModelSerializer):
    questions = FormQuestionSerializer(many=True)

    class Meta:
        model = IdeaForm
        fields = ['id', 'title', 'questions']

#//////////////////////////// CREATE AND EDIT FORM ////////////////////////////////


class IdeaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = ['title', 'description', 'answers']

#/////////////////////////// PUBLISH FORM /////////////////////////////////

class IdeaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = [
            'id',
            'title',
            'description',
            'status',
            'answers',
            'created_at'
        ]


