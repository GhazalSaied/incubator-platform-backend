from rest_framework import serializers
from .models import (
    Evaluation, 
    IncubationReview,
    EvaluationScore,
    EvaluationNote,

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
            "progress_score",
            "notes",
            "is_submitted",
            "submitted_at",
            "created_by",
        ]

        read_only_fields = [
            "id",
            "is_submitted",
            "submitted_at",
            "created_at",
        ]

#/////////////////////////// EVALUATION NOTES //////////////////////

class EvaluationNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationNote
        fields = [
            "id",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

#//////////////////// REJECTED IDEA NOTES ////////////////////

class RejectedIdeaNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = EvaluationNote

        fields = [
            "note",
        ]

        read_only_fields = fields
        

#//////////////////////////// LATEST INCUBATION NOTES ////////////////////////

class IncubationLatestNotesSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncubationReview

        fields = [
            "notes",
            "submitted_at",
        ]


#///////////////////////// FORM OPEN SERIALIZER /////////////////////

class EvaluationFormSerializer(serializers.Serializer):
    is_published = serializers.BooleanField()
    criteria = serializers.ListField()
    scores = serializers.ListField()
    is_submitted = serializers.BooleanField()

#////////////////// EVALUATION SESSION STATUS > مرحلة التقييم في تاب مراحل الاحتضان ////////////////

class EvaluationSessionStatusSerializer(
    serializers.Serializer
):
    meeting_date = serializers.DateTimeField()
    status = serializers.CharField()


#///////////////////// INCUBATION PHASE > تاب مراحل الاحتضان //////////////////////

class IncubationOverviewSerializer(
    serializers.Serializer
):
    next_meeting_date = serializers.DateTimeField(
        allow_null=True
    )

    notes = IncubationLatestNotesSerializer(
        many=True
    )