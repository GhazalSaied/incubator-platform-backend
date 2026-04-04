from rest_framework import serializers
from .models import (
    Evaluation, 
    IncubationReview,
    EvaluationScore,

)



#/////////////////////// EVALUATION SCORE //////////////////

class EvaluationScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationScore
        fields = ["criterion", "score"]

        

#////////////////////////  EVALUATION /////////////////////

class EvaluationSerializer(serializers.ModelSerializer):
    scores = EvaluationScoreSerializer(many=True)

    class Meta:
        model = Evaluation
        fields = [
            "id",
            "idea",
            "notes",
            "scores",
            "is_submitted",
        ]

    def create(self, validated_data):
        scores_data = validated_data.pop("scores")
        evaluation = Evaluation.objects.create(**validated_data)

        for score_data in scores_data:
            EvaluationScore.objects.create(
                evaluation=evaluation,
                **score_data
            )

        return evaluation

    def update(self, instance, validated_data):
        scores_data = validated_data.pop("scores", None)

        instance.notes = validated_data.get("notes", instance.notes)
        instance.save()

        if scores_data:
            for score_data in scores_data:
                EvaluationScore.objects.update_or_create(
                    evaluation=instance,
                    criterion=score_data["criterion"],
                    defaults={"score": score_data["score"]}
                )

        return instance

#//////////////////////////// INCUBATION REVIEW //////////////////

class IncubationReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncubationReview
        fields = [
            "meeting_date",
            "progress_score",
            "notes"
        ]

