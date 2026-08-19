from rest_framework import serializers

from ideas.models import Idea
from evaluations.models import EvaluationInvitation,EvaluationCriterion


#\\\\\\\\\\\\\\\AssignmentDashboardSerializer\\\\\\\\\\\\\\\\\\\\\\\
class AssignmentDashboardSerializer(serializers.ModelSerializer):

    evaluators = serializers.SerializerMethodField()
    sector = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "sector",
            "target_audience",
            "evaluators",
        ]
    def get_sector(self, obj):
        return obj.sector or "غير محدد"
    def get_evaluators(self, obj):

        assignments = obj.evaluation_assignments.all()

        if not assignments.exists():
            return []

        return [
        {
            "id": assignment.evaluator.id,
            "name": assignment.evaluator.full_name
        }
        for assignment in assignments
    ]
        
        
#\\\\\\\\\\\\\\\\SeasonEvaluatorSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class SeasonEvaluatorSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(source="user.full_name")

    specialization = serializers.SerializerMethodField()
    primary_skills = serializers.SerializerMethodField()
    additional_skills = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source="user.id")
    class Meta:
        model = EvaluationInvitation
        fields = [
            "id",
            "user_id",
            "season",
            "full_name",
            "specialization",
            "primary_skills",
            "additional_skills",
        ]

    def get_specialization(self, obj):
        profile = getattr(obj.user, "volunteer_profile", None)
        return profile.specialization if profile else None

    def get_primary_skills(self, obj):
        profile = getattr(obj.user, "volunteer_profile", None)
        if not profile:
            return None
        return profile.get_primary_skills_display()

    def get_additional_skills(self, obj):
        profile = getattr(obj.user, "volunteer_profile", None)
        if not profile:
            return []
        return profile.additional_skills
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\AssignEvaluatorsSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class AssignEvaluatorsSerializer(serializers.Serializer):

    evaluators_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        error_messages={
            "required": "يجب اختيار مقيم واحد على الأقل",
            "empty": "يجب اختيار مقيم واحد على الأقل",
        }
    )
    
#\\\\\\\\\\\\\\\\\\\\\\\\MeetingDashboardSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class MeetingDashboardSerializer(serializers.ModelSerializer):

    has_evaluators = serializers.SerializerMethodField()
    meeting_date = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "sector",
            "target_audience",
            "has_evaluators",
            "meeting_date"  
        ]

    def get_has_evaluators(self, obj):
        return obj.evaluation_assignments.exists()

    def get_meeting_date(self, obj):
        assignments = obj.evaluation_assignments.all()

        # فلترة اللي عندهم موعد
        dates = [
            a.meeting_date for a in assignments
            if a.meeting_date is not None
        ]

        if not dates:
            return " "

        # رجع أقرب موعد
        return min(dates).strftime("%Y/%m/%d %H:%M")
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\EvaluatorInfoSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class EvaluatorInfoSerializer(serializers.Serializer):

    id = serializers.IntegerField(source="evaluator.id")
    name = serializers.CharField(source="evaluator.full_name")
    image = serializers.ImageField(source="evaluator.avatar")
    specialization = serializers.CharField(
        source="evaluator.volunteer_profile.specialization"
    )
    
#\\\\\\\\\\\\\\\\\\\SetMeetingSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class SetMeetingSerializer(serializers.Serializer):
    date = serializers.DateField(
        error_messages={
            "required": "الرجاء تحديد تاريخ التقييم",
            "invalid": "تاريخ التقييم غير صالح",
        }
    )

    time = serializers.TimeField(
        error_messages={
            "required": "الرجاء تحديد وقت التقييم",
            "invalid": "وقت التقييم غير صالح",
        }
    )
    
#\\\\\\\\\\\\\\EvaluationCriteriaSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class EvaluationCriteriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = EvaluationCriterion
        fields = ["id", "title", "max_score", "is_active"]
        
        
    