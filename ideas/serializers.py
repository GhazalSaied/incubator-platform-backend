from rest_framework import serializers
from .models import (Idea, FormQuestion, 
                     IdeaForm, Season,
                     TeamRequest
)

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
            'sector',
            'target_audience',
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
        
        
        
#\\\\\\\\SeasonSerializer\\\\\
class SeasonSerializer(serializers.ModelSerializer):
    ideas_count = serializers.SerializerMethodField()

    class Meta:
        model = Season
        fields = "__all__"

    def get_ideas_count(self, obj):
        return obj.idea_set.count()
    
    
#\\\\\SeasonCreateSerializer\\\\\
class SeasonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            "name",
            "start_date",
            "end_date",
            "is_open",
        ]

    def validate(self, data):
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError(
                "تاريخ البداية يجب أن يكون قبل النهاية"
            )
        return data
    
#\\\\\\SeasonPublishSerializer\\\\
class SeasonPublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ["is_published"]

    def update(self, instance, validated_data):
        instance.is_published = True
        instance.save()
        return instance