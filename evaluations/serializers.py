from rest_framework import serializers
from .models import (
    Evaluation, 
    IncubationReview,

)



#////////////////////////  EVALUATION /////////////////////

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = [
            "id",
            "idea",
            "score",
            "notes",
            "is_submitted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["is_submitted", "created_at", "updated_at"]

#//////////////////////////// INCUBATION REVIEW //////////////////

class IncubationReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncubationReview
        fields = [
            "meeting_date",
            "progress_score",
            "notes"
        ]