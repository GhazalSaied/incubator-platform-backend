from rest_framework import serializers
from ideas.models import Idea
from django.utils import timezone
from evaluations.models import EvaluationSession
from datetime import datetime
class IdeaEvaluationListSerializer(serializers.ModelSerializer):
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
        evaluators = obj.assigned_evaluators.filter(status="accepted")

        return [
            ev.evaluator.full_name
            for ev in evaluators
        ]
        




class ScheduleEvaluationSerializer(serializers.Serializer):
    date = serializers.DateField()
    time = serializers.TimeField()

    def validate(self, data):
        idea = self.context.get("idea")

        # 🔥 دمج التاريخ والوقت
        scheduled_at = datetime.combine(data["date"], data["time"])

        # 🔥 timezone awareness
        scheduled_at = timezone.make_aware(scheduled_at)

        # ❌ منع الماضي
        if scheduled_at <= timezone.now():
            raise serializers.ValidationError("لا يمكن تحديد موعد في الماضي")

        # ❌ لازم في مقيمين accepted
        evaluators_qs = idea.assigned_evaluators.filter(status="accepted")

        if not evaluators_qs.exists():
            raise serializers.ValidationError("لا يوجد مقيمين موافقين لهذه الفكرة")

        # ❌ منع تكرار جلسة لنفس الفكرة
        if EvaluationSession.objects.filter(idea=idea).exists():
            raise serializers.ValidationError("تم تحديد موعد مسبق لهذه الفكرة")

        # ❌ منع تضارب مواعيد للمقيمين
        evaluator_ids = evaluators_qs.values_list("evaluator_id", flat=True)

        conflict_exists = EvaluationSession.objects.filter(
            scheduled_at=scheduled_at,
            idea__assigned_evaluators__evaluator_id__in=evaluator_ids,
            idea__assigned_evaluators__status="accepted"
        ).exists()

        if conflict_exists:
            raise serializers.ValidationError("أحد المقيمين لديه جلسة بنفس الوقت")

        data["scheduled_at"] = scheduled_at
        return data