from rest_framework import serializers
from .models import (Idea, FormQuestion, 
                     IdeaForm, Season,
                     TeamRequest,
                     FormQuestionChoice
)
from ideas.services.season_phase_service import SeasonPhaseService

#///////////////////////////IDAE FORM SERIALIZER /////////////////////////////////

class FormQuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormQuestionChoice
        fields = ["value", "label"]


class FormQuestionSerializer(serializers.ModelSerializer):
    choices = FormQuestionChoiceSerializer(many=True)
    class Meta:
        model = FormQuestion
        fields = ['id','key','label','type','required','order','choices','placeholder', 'help_text']


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

#//////////////////////// IDEA FOR EVALUATER ///////////////////////


class IdeaForEvaluationSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)
    form = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "description",
            "status",
            "owner_name",
            "answers",
            "form",
            "created_at",
        ]

    def get_form(self, obj):
        season = getattr(obj, "season", None)
        if not season or not hasattr(season, "form"):
            return None

        return IdeaFormSerializer(season.form).data


#//////////////////////////////IDEA LIST (VIEW ONLY)/////////////////////////////////////

class MyIdeaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "status",
            "created_at",
        ]

#/////////////////////////// IDEA DASHBOARD SERIALIZER /////////////////////////

class IdeaDashboardSerializer(serializers.Serializer):
    phase = serializers.CharField()
    progress = serializers.ListField()
    data = serializers.DictField()
    
#//////////////////////////// EXHIBITION  /////////////////////////////

class ExhibitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Idea
        fields = [
            "title",
            "exhibition_image",
            "project_goal",
            "project_services",
            "contact_email"
        ]

#/////////////////////////// TEAM REQUEST SERIALIZER /////////////////////

class TeamRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamRequest
        fields = "__all__"
        
        
 #\\\\\\\\\\\\\\\\\\SeasonStatusSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class SeasonStatusSerializer(serializers.Serializer):
    is_open = serializers.BooleanField()
    label = serializers.CharField()
    phase = serializers.CharField(allow_null=True)       
        
        
#\\\\\\\\SeasonSerializer\\\\\
class SeasonListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    ideas_count = serializers.IntegerField()
    status = SeasonStatusSerializer()
    
#\\\\\SeasonCreateSerializer\\\\\
class SeasonCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
#\\\\\\SeasonPublishSerializer\\\\
class SeasonPublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ["is_published"]

    def update(self, instance, validated_data):
        instance.is_published = True
        instance.save()
        return instance
    
    
    
#\\\\\\\\\\\\\\\IdeaListSerialize\\\\\\\\\\\
class IdeaListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "status",
            "owner_name",
            "created_at",
        ]
        
        
#\\\\\\\\\\\\\\\\\\\\\SeasonDetailsSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class SeasonDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    ideas_count = serializers.IntegerField()
    phase = serializers.CharField()
    can_edit = serializers.BooleanField()
    remaining_days = serializers.IntegerField(allow_null=True)
    evaluation_ideas_count = serializers.IntegerField(allow_null=True)
    
class ChoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    label = serializers.CharField()
    order = serializers.IntegerField()


class QuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField()
    label = serializers.CharField()
    type = serializers.CharField()
    required = serializers.BooleanField()
    order = serializers.IntegerField()
    choices = ChoiceSerializer(many=True)


class FormSerializer(serializers.Serializer):
    title = serializers.CharField()
    questions = QuestionSerializer(many=True)

class SeasonInfoSerializer(serializers.Serializer):
    season_name = serializers.CharField()
    phase = serializers.CharField()
    ideas_count = serializers.IntegerField()

    remaining_days = serializers.IntegerField(required=False)
    evaluation_ideas_count = serializers.IntegerField(required=False)

    show_remaining_days = serializers.BooleanField()
    show_evaluation_count = serializers.BooleanField()
class SeasonFormDesignSerializer(serializers.Serializer):
    season_info = SeasonInfoSerializer()
    form = FormSerializer()
    
class IdeaRowSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project_name = serializers.CharField()
    submitted_by = serializers.CharField()
    submitted_at = serializers.DateTimeField()


class SeasonReviewSerializer(serializers.Serializer):
    season_info = SeasonInfoSerializer()
    ideas = IdeaRowSerializer(many=True)   


# serializers.py

from rest_framework import serializers


class CreateQuestionSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    type = serializers.ChoiceField(choices=[
        "text",
        "number",
        "select",
        "select_multiple",
        "boolean"
    ])
    required = serializers.BooleanField(default=False)
    order = serializers.IntegerField(required=False)
    
    
class CreateChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
    order = serializers.IntegerField(required=False)
    
    
class UpdateChoiceSerializer(serializers.Serializer):
    value = serializers.CharField(required=False)
    label = serializers.CharField(required=False)