from rest_framework import serializers
from .models import VolunteerProfile, VolunteerAvailability , ConsultationRequest,VolunteerJoinRequest


#///////////////////////////////// VolunteerAvailabilitySerializer  ///////////////////////////


class VolunteerAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerAvailability
        fields = ["day", "start_time", "end_time"]

#////////////////////////////// VolunteerProfile Serializer ///////////////////

class VolunteerProfileSerializer(serializers.ModelSerializer):
    availabilities = VolunteerAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = VolunteerProfile
        fields = [
            "id",
            "status",
            "residence",
            "years_of_experience",
            "primary_skills",
            "additional_skills",
            "volunteer_type",
            "availability_type",
            "motivation",
            "cv",
            "availabilities",
        ]
#////////////////////////////// AVAILABLITY UPDATE / CREATE/////////////////////////

class VolunteerAvailabilityCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerAvailability
        fields = ["id", "day", "start_time", "end_time"]

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "وقت البداية يجب أن يكون قبل وقت النهاية"
            )
        return data
    
#///////////////////////////////// ConsultationRequestSerializer ///////////////////////////////////////

class ConsultationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationRequest
        fields = [
            "id",
            "requester_name",
            "requester_email",
            "project_title",
            "consultation_type",
            "description",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]


#////////////////////////////////// VolunteerJoinRequestSerializer ///////////////////////////////////////////////////////


class VolunteerJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerJoinRequest
        fields = [
            "id",
            "requester_name",
            "requester_email",
            "project_title",
            "description",
            "target_audience",
            "problem_statement",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]


#/////////////////////////////////// VOLUNTEER DASHBOARD  /////////////////////////////////////////////////

class VolunteerDashboardSerializer(serializers.Serializer):
    profile = VolunteerProfileSerializer()
    availability = VolunteerAvailabilitySerializer(many=True)
    consultations = serializers.DictField()