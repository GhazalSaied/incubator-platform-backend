from rest_framework import serializers
from .models import BootcampSession, BootcampAbsenceRequest, BootcampAttendance
from admin_panel.bootcamp.sessions.services import BootcampSessionQueryService
from django.db.models import Q
from ideas.models import Idea, IdeaStatus
from datetime import datetime



#/////////////////////////// BOOTCAMP SESSION ////////////////////////
class BootcampSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()


class BootcampSessionsTableSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(
        source="trainer.full_name",
        default=None
    )
    time_range = serializers.SerializerMethodField()
    session_status = serializers.SerializerMethodField()

    class Meta:
        model = BootcampSession
        fields = [
            "id",
            "title",
            "date",
            "trainer_name",
            "time_range",
            "tasks",
            "session_status",
        ]

    def get_time_range(self, obj):
        if not obj.start_time or not obj.end_time:
            return None

        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"

    def get_session_status(self, obj):
        if not obj.date or not obj.start_time:
            return "لم تأت بعد"

        session_datetime = datetime.combine(
            obj.date,
            obj.start_time
        )

        if session_datetime < datetime.now():
            return "انتهت"

        return "لم تأت بعد"


#/////////////////////////////// NEXT BOOTCAMP SESSION //////////////////////////////

class NextBootcampSessionSerializer(serializers.ModelSerializer):
    time_range = serializers.SerializerMethodField()


    class Meta:
        model = BootcampSession
        fields = [
            "id",
            "title",
            "date",
            "time_range",
            "location",
            "tasks",
        ]

    def get_time_range(self, obj):
        if not obj.start_time or not obj.end_time:
            return None

        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    

#////////////////////////// BOOTCAMP ABSENCE REQUEST ////////////////////

class BootcampAbsenceRequestCreateSerializer(serializers.Serializer):
   
    reason = serializers.CharField()

    def validate_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Reason is required."
            )
        return value.strip()


#/////////////////////////// VOLUNTEER BOOTCAMP SESSIONS > TRAINER /////////////////

class VolunteerBootcampSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BootcampSession
        fields = [
            "id",
            "title",
            "date",
            "start_time",
            "end_time",
            "tasks",
            "location",
        ]

#/////////////////////// BOOTCAMP IDEA ATTENDANCE LIST ////////////////

class BootcampIdeaAttendanceListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.full_name")

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "owner_name",
        ]

#///////////////////////// BOOTCAMP IDEA ATTENDANCE CREATE ////////////////

class BootcampAttendanceCreateSerializer(serializers.Serializer):
    STATUS_PRESENT = "present"
    STATUS_ABSENT = "absent"

    STATUS_CHOICES = (
        (STATUS_PRESENT, "Present"),
        (STATUS_ABSENT, "Absent"),
    )

    idea_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=STATUS_CHOICES
    )

    def validate(self, attrs):
        session = self.context["session"]
        request_user = self.context["request"].user
        idea_id = attrs["idea_id"]

        if session.trainer_id != request_user.id:
            raise serializers.ValidationError(
                "You are not allowed to manage this session."
            )

        try:
            idea = Idea.objects.get(
                id=idea_id,
                status=IdeaStatus.BOOTCAMP
            )
        except Idea.DoesNotExist:
            raise serializers.ValidationError(
                "Idea not found or not in BOOTCAMP status."
            )

        already_exists = BootcampAttendance.objects.filter(
            session=session,
            idea=idea
        ).exists()

        if already_exists:
            raise serializers.ValidationError(
                "Attendance already submitted for this idea."
            )

        attrs["idea"] = idea
        return attrs






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