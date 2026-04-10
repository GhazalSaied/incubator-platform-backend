from rest_framework import serializers

from ideas.models import Idea
from evaluations.models import EvaluationInvitation,EvaluationCriterion


#\\\\\\\\\\\\\\\AssignmentDashboardSerializer\\\\\\\\\\\\\\\\\\\\\\\
class AssignmentDashboardSerializer(serializers.ModelSerializer):

    evaluators = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "sector",
            "target_audience",
            "evaluators",
        ]

    def get_evaluators(self, obj):

        assignments = obj.evaluation_assignments.all()

        if not assignments.exists():
            return []

        return [
            assignment.evaluator.full_name
            for assignment in assignments
        ]
        
        
#\\\\\\\\\\\\\\\\SeasonEvaluatorSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

from rest_framework import serializers


class SeasonEvaluatorSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(
        source="user.full_name"
    )

    volunteer_type = serializers.CharField(
        source="user.volunteer_profile.volunteer_type"
    )

    primary_skills = serializers.CharField(
        source="user.volunteer_profile.primary_skills"
    )

    additional_skills = serializers.CharField(
        source="user.volunteer_profile.additional_skills"
    )


    class Meta:
        model = EvaluationInvitation
        fields = [
            "id",
            "full_name",
            "volunteer_type",
            "primary_skills",
            "additional_skills",
        ]
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\AssignEvaluatorsSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class AssignEvaluatorsSerializer(serializers.Serializer):

    idea_id = serializers.IntegerField()

    evaluators_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
    
#\\\\\\\\\\\\\\\\\\\\\\\\MeetingDashboardSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class MeetingDashboardSerializer(serializers.ModelSerializer):

    has_evaluators = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "sector",
            "target_audience",
            "has_evaluators"
        ]

    def get_has_evaluators(self, obj):
        return obj.evaluation_assignments.exists()
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\EvaluatorInfoSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class EvaluatorInfoSerializer(serializers.Serializer):

    id = serializers.IntegerField(source="evaluator.id")
    name = serializers.CharField(source="evaluator.full_name")
    image = serializers.ImageField(source="evaluator.avatar")
    specialization = serializers.CharField(
        source="evaluator.volunteer_profile.volunteer_type"
    )
    
#\\\\\\\\\\\\\\\\\\\SetMeetingSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class SetMeetingSerializer(serializers.Serializer):
    idea_id = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.TimeField()
    
    
#\\\\\\\\\\\\\\EvaluationCriteriaSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class EvaluationCriteriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = EvaluationCriterion
        fields = ["id", "title", "max_score", "is_active"]