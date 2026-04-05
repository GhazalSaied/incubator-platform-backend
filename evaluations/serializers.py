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
        read_only_fields = ["id", "is_submitted"]
        

#//////////////////////////// INCUBATION REVIEW //////////////////

class IncubationReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncubationReview
        fields = [
            "meeting_date",
            "progress_score",
            "notes"
        ]

