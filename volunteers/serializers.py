from rest_framework import serializers
from .models import VolunteerProfile, VolunteerAvailability


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
