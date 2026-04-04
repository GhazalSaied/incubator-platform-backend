from rest_framework import serializers
from .models import BootcampSession,BootcampAbsenceRequest, BootcampAttendance
from ideas.models import Idea


#/////////////////////////// BOOTCAMP SESSION ////////////////////////
class BootcampSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BootcampSession
        fields = [
            "id",
            "title",
            "trainer",
            "season",
            "date",
            "start_time",
            "end_time",
            "tasks",
            "location",
        ]

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "وقت البداية يجب أن يكون قبل النهاية"
            )
        return data


# 🔹 Attendance
class SessionAttendanceSerializer(serializers.ModelSerializer):
    idea_title = serializers.CharField(source="idea.title", read_only=True)

    class Meta:
        model = BootcampAttendance
        fields = ["id", "idea", "idea_title", "status"]


# 🔹 Decision (input)
class BootcampDecisionSerializer(serializers.Serializer):
    idea_id = serializers.IntegerField()
    decision = serializers.ChoiceField(choices=["approve", "reject"])
    message = serializers.CharField()
    
#\\\\\\\ BootcampIdeaList\\\\\\\\\
class BootcampIdeaListSerializer(serializers.Serializer):
    idea_id = serializers.IntegerField()
    idea_title = serializers.CharField()
    absence_percentage = serializers.FloatField()
    commitment_status = serializers.CharField()
    bootcamp_status = serializers.CharField()

#\\\\\\AbsenceRequest\\\\\\\\


class AbsenceRequestSerializer(serializers.ModelSerializer):
    idea_title = serializers.CharField(source="idea.title", read_only=True)
    applicant = serializers.CharField(source="idea.owner.full_name", read_only=True)
    session_date = serializers.DateField(source="session.date", read_only=True)

    class Meta:
        model = BootcampAbsenceRequest
        fields = [
            "id",
            "idea_title",
            "applicant",
            "session_date",
            "reason",
            "status"
        ]

#\\\\\\\AbsenceDecision\\\\\\\\\\\\\\\\\\\
class AbsenceDecisionSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    decision = serializers.ChoiceField(choices=["approve", "warn"])
    
    
    
 #\\\\\   AttendanceStats\\\\\\\\\
class AttendanceStatsSerializer(serializers.Serializer):
    total_sessions = serializers.IntegerField()
    absent_sessions = serializers.IntegerField()
    absence_percentage = serializers.FloatField()
    
  #\\\\\\\\\\  BootcampParticipant\\\\\\\\\\
class BootcampParticipantSerializer(serializers.Serializer):
    idea_id = serializers.IntegerField()
    idea_title = serializers.CharField()
    owner = serializers.CharField()
    commitment_percentage = serializers.FloatField()
    bootcamp_status = serializers.CharField()