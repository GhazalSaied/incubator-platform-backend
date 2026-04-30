from rest_framework import serializers
from .models import BootcampSession, BootcampAbsenceRequest, BootcampAttendance
from ideas.models import Idea
from admin_panel.bootcamp.sessions.services import BootcampSessionQueryService

# USER SIDE 


#/////////////////////////// BOOTCAMP SESSION ////////////////////////
class BootcampSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    time_range = serializers.SerializerMethodField()

    class Meta:
        model = BootcampSession
        fields = [
            "id",
            "title",
            "trainer",
            "trainer_name",
            "date",
            "time_range",
            "tasks",
            "location",
        ]

    def get_trainer_name(self, obj):
        return BootcampSessionQueryService.get_trainer_name(obj)

    def get_time_range(self, obj):
        return BootcampSessionQueryService.get_time_range(obj)

    def validate(self, data):
        start = data.get("start_time")
        end = data.get("end_time")

        if start and end and start >= end:
            raise serializers.ValidationError(
                "وقت البداية يجب أن يكون قبل النهاية"
            )
        return data
    





# ///////////////////// ADMIN ///////////////////////////////


#  Attendance
class SessionAttendanceSerializer(serializers.ModelSerializer):
    idea_title = serializers.CharField(source="idea.title", read_only=True)

    class Meta:
        model = BootcampAttendance
        fields = ["id", "idea", "idea_title", "status"]





class BootcampDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["approve", "reject"])
    
    
    
#\\\\\\\ BootcampIdeaList\\\\\\\\\
class BootcampIdeaListSerializer(serializers.Serializer):
    idea_id = serializers.IntegerField()
    idea_title = serializers.CharField()
    absence_percentage = serializers.FloatField()
    commitment_status = serializers.CharField()
    
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