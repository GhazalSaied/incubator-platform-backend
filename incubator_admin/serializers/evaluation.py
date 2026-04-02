from rest_framework import serializers
from ideas.models import Idea


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