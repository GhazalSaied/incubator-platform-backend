from rest_framework import serializers
from django.db import transaction
from .models import (VolunteerProfile, 
                     VolunteerAvailability , 
                     ConsultationRequest,
                     Workshop,
                     JoinRequest
                     )
from ideas.services.idea_service import IdeaService
from ideas.models import  TeamStatus ,SuggestedVolunteer
from messaging.models import Conversation

#///////////////////////////////// VolunteerAvailabilitySerializer  ///////////////////////////


class VolunteerAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerAvailability
        fields = ["day", "start_time", "end_time"]

#////////////////////////////// VolunteerProfile Serializer ///////////////////

class VolunteerProfileSerializer(serializers.ModelSerializer):
    availabilities = VolunteerAvailabilitySerializer(many=True, read_only=True)
    name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = VolunteerProfile
        fields = [
            "id",
            "name",
            "email",
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
    

        volunteer = self.instance.volunteer if self.instance else self.context["request"].user.volunteer_profile

        overlaps = VolunteerAvailability.objects.filter(
            volunteer=volunteer,
            day=data["day"],
            start_time__lt=data["end_time"],
            end_time__gt=data["start_time"]
        )

        if self.instance:
            overlaps = overlaps.exclude(id=self.instance.id)

        if overlaps.exists():
            raise serializers.ValidationError("يوجد تداخل في الأوقات")

        return data
    
#/////////////////////////////////CREATE CONSULTATION REQUEST ///////////////////////////////////////


class CreateConsultationRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultationRequest
        fields = [
            "required_skill",
            "description",
            "help_type",

        ]

    def validate(self, data):

        request = self.context["request"]
        user = request.user

        volunteer_user_id = self.context["volunteer_user_id"]

        idea = IdeaService.get_dashboard_idea(user)

        if not idea:
            raise serializers.ValidationError("يجب أن تكون مرتبطًا بفكرة لإرسال طلب استشارة")
        
        try:
            volunteer = VolunteerProfile.objects.select_related("user").get(
                user_id=volunteer_user_id,
                status=VolunteerProfile.APPROVED
            )

        except VolunteerProfile.DoesNotExist:
            raise serializers.ValidationError(
                "المتطوع غير موجود"
            )

        if volunteer.user_id == user.id:
            raise serializers.ValidationError(
                "لا يمكنك إرسال طلب لنفسك"
            )
        
        if not data.get("help_type"):
            raise serializers.ValidationError("نوع المساعدة مطلوب")
        
        if data.get("help_type") not in dict(ConsultationRequest.HELP_TYPE_CHOICES):
            raise serializers.ValidationError("نوع المساعدة غير صالح")
        
        if not data.get("required_skill"):
            raise serializers.ValidationError("نوع الاستشارة مطلوب")


        #  منع تكرار طلب الاستشارة
        if ConsultationRequest.objects.filter(
            requester=user,
            volunteer=volunteer,
            idea=idea,
            status=ConsultationRequest.PENDING
        ).exists():
            raise serializers.ValidationError("لديك طلب استشارة قيد الانتظار")
        

        data["volunteer"] = volunteer
        data["idea"] = idea
       

        return data

#///////////////////////////////// CONSULTATION REQUEST ///////////////////////////////////////

class ConsultationRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source="requester.full_name", read_only=True)
    requester_email = serializers.EmailField(source="requester.email", read_only=True)
    requester_id = serializers.IntegerField(source="requester.id",read_only=True)
    idea_title = serializers.CharField(source="idea.title", read_only=True)


    class Meta:
        model = ConsultationRequest
        fields = [
            "id",
            "required_skill",
            "help_type",
            "description",
            "requester_name",
            "requester_email",
            "requester_id",
            "idea_title",
            "status",
        ]


#////////////////////////// CREATE JOIN REQUEST //////////////////////

class CreateJoinRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = JoinRequest
        fields = [
            "description",
            "tasks",
            "required_skill",
        ]

    def validate(self, attrs):

        request = self.context["request"]
        user = request.user

        volunteer_user_id = self.context["volunteer_user_id"]

        idea = IdeaService.get_user_idea(user)

        if not idea:
            raise serializers.ValidationError(
                "لا توجد فكرة مرتبطة بهذا المستخدم"
            )

        team_request = (
            idea.team_requests.filter(
                status="APPROVED"
            )
            .order_by("-created_at")
            .first()
        )

        if not team_request:
            raise serializers.ValidationError(
                "لا يوجد طلب فريق مقبول"
            )


        try:
            volunteer = VolunteerProfile.objects.select_related("user").get(
                user_id=volunteer_user_id,
                status=VolunteerProfile.APPROVED
            )

        except VolunteerProfile.DoesNotExist:
            raise serializers.ValidationError(
                "المتطوع غير موجود"
            )

        if volunteer.user_id == user.id:
            raise serializers.ValidationError(
                "لا يمكنك إرسال طلب لنفسك"
            )

        is_suggested = SuggestedVolunteer.objects.filter(
            team_request=team_request,
            volunteer=volunteer
        ).exists()

        if not is_suggested:
            raise serializers.ValidationError(
                "المتطوع غير مقترح لهذا الطلب"
            )

        has_pending_request = JoinRequest.objects.filter(
            requester=user,
            volunteer=volunteer,
            status=JoinRequest.PENDING,
        ).exists()

        if has_pending_request:
            raise serializers.ValidationError(
                "لديك طلب انضمام قيد الانتظار لهذا المتطوع"
            )

        has_rejected_request = JoinRequest.objects.filter(
            requester=user,
            volunteer=volunteer,
            status=JoinRequest.REJECTED,
        ).exists()

        if has_rejected_request:
            raise serializers.ValidationError(
                "لا يمكن إعادة إرسال الطلب لهذا المتطوع"
            )

        attrs["volunteer"] = volunteer
        attrs["idea"] = idea
        attrs["team_request"] = team_request
        attrs["requester"] = user

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        return JoinRequest.objects.create(**validated_data)

#/////////////////////////// JOIN REQUEST (RESPONSE) /////////////////////////////

class JoinRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source="requester.full_name", read_only=True)
    requester_email = serializers.EmailField(source="requester.email", read_only=True)
    idea_title = serializers.CharField(source="idea.title", read_only=True)
    required_skill = serializers.CharField(read_only=True)

    class Meta:
        model = JoinRequest
        fields = [
            "id",
            "status",
            "requester_name",
            "requester_email",
            "idea_title",
            "required_skill",
        ]

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

#/////////////////// CREATE WORKSHOP SERIALIZER ////////////////////////

class CreateWorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = [
            "id",
            "title",
            "category",
            "objectives",
            "target_audience",
            "description",
            "capacity",
            "sessions",
            "start_date",
            "end_date",
            "days",
            "time_from",
            "time_to",
            "image"
        ]

    def validate(self, data):
        request = self.context.get("request")

        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError("تاريخ البداية يجب أن يكون قبل النهاية")

        if data["time_from"] >= data["time_to"]:
            raise serializers.ValidationError("وقت البداية يجب أن يكون قبل النهاية")

        if not data.get("days"):
            raise serializers.ValidationError("يجب تحديد الأيام")
        
        if Workshop.objects.filter(
            created_by=request.user,
            status="PENDING",
            title=data["title"],
            objectives=data["objectives"],
            target_audience=data["target_audience"],
        ).exists():
            raise serializers.ValidationError(
                "لديك طلب مشابه قيد المراجعة"
            )

        return data
    
#///////////////////////////// CONSULTANTS LIST //////////////////////////////

class ConsultantListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name")
    avatar = serializers.ImageField(source="user.avatar")
    availability = VolunteerAvailabilitySerializer(
        source="availabilities",
        many=True
    )
    user_id = serializers.IntegerField(
        source="user.id",
        read_only=True
    )

    class Meta:
        model = VolunteerProfile
        fields = [

            "user_id",
            "full_name",
            "avatar",
            "primary_skills",
            "availability",
        ]