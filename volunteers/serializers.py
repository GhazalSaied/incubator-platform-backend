from rest_framework import serializers
from .models import (VolunteerProfile, 
                     VolunteerAvailability , 
                     ConsultationRequest,
                     )
from ideas.services.idea_service import IdeaService


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
    
#/////////////////////////////////CREATE CONSULTATION REQUEST ///////////////////////////////////////

class CreateConsultationRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultationRequest
        fields = [
            "volunteer",
            "request_type",
            "description",
            "team_request",
        ]

    def validate(self, data):

        user = self.context["request"].user
        idea = IdeaService.get_user_idea(user)

        if data["volunteer"].user == user:
            raise serializers.ValidationError("لا يمكنك إرسال طلب لنفسك")

        data["idea"] = idea

        request_type = self.initial_data.get("request_type")
        if request_type == "JOIN":

            team_request = idea.team_requests.filter(
                status="APPROVED"
            ).order_by("-created_at").first()


            if idea.team_status == "team_full":
                raise serializers.ValidationError("الفريق مكتمل")
            
            if ConsultationRequest.objects.filter(
                requester=user,
                volunteer=data["volunteer"],
                idea=idea,
                request_type="JOIN",
                status="PENDING"
            ).exists():
                raise serializers.ValidationError("لديك طلب انضمام قيد الانتظار")
                            
            if not team_request:
                raise serializers.ValidationError("لا يوجد طلب فريق فعال")

            data["team_request"] = team_request

        return data

#///////////////////////////////// CONSULTATION REQUEST ///////////////////////////////////////

class ConsultationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationRequest
        fields = [
            "id",
            "volunteer",
            "idea",
            "request_type",
            "description",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]



#/////////////////////////////////// VOLUNTEER DASHBOARD  /////////////////////////////////////////////////

class VolunteerDashboardSerializer(serializers.Serializer):
    profile = VolunteerProfileSerializer()
    availability = VolunteerAvailabilitySerializer(many=True)
    consultations = serializers.DictField()



#/////////////////////////////// Assigned Projects Serializer  //////////////////////////////////////

class AssignedProjectsSerializer(serializers.Serializer):
    consultations = serializers.ListField()
    ongoing = serializers.ListField()
    joined_projects = serializers.ListField()