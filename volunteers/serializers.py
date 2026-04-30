from rest_framework import serializers
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
    email = serializers.EmailField(source="user.email", read_only=True)

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
            "volunteer",
            "required_skill",
            "description",
            "help_type",

        ]

    def validate(self, data):

        user = self.context["request"].user
        idea = IdeaService.get_user_idea(user)

        if not idea:
            raise serializers.ValidationError("يجب أن تكون مرتبطًا بفكرة لإرسال طلب استشارة")
        
        volunteer = data.get("volunteer")

        if isinstance(volunteer, int):
            try:
                volunteer = VolunteerProfile.objects.get(id=volunteer)
            except VolunteerProfile.DoesNotExist:
                raise serializers.ValidationError("المتطوع غير موجود")

        if volunteer.user == user:
            raise serializers.ValidationError("لا يمكنك إرسال طلب لنفسك")
        
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
    idea_title = serializers.CharField(source="idea.title", read_only=True)
    conversation_id = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationRequest
        fields = [
            "id",
            "required_skill",
            "help_type",
            "description",
            "status",
            "created_at",
            "requester_name",
            "requester_email",
            "idea_title",
            "conversation_id",
        ]

    def get_conversation_id(self, obj):
        if obj.status != ConsultationRequest.ACCEPTED:
            return None

        conversation = Conversation.objects.filter(
            participants=obj.volunteer.user
        ).filter(
            participants=obj.requester
        ).first()

        return conversation.id if conversation else None

#////////////////////////// CREATE JOIN REQUEST //////////////////////

class CreateJoinRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = JoinRequest
        fields = [
            "volunteer",
            "description",
            "tasks",
            "required_skill",
        ]

    def validate(self, data):
        user = self.context["request"].user
        idea = IdeaService.get_user_idea(user)

        if not idea:
            raise serializers.ValidationError("لا يوجد فكرة مرتبطة")

        volunteer = data.get("volunteer")

        if isinstance(volunteer, int):

            try:
                volunteer = VolunteerProfile.objects.get(id=volunteer)
            except VolunteerProfile.DoesNotExist:
                raise serializers.ValidationError("المتطوع غير موجود")
            

        if volunteer.user == user:
            raise serializers.ValidationError("لا يمكنك إرسال طلب لنفسك") 
        
        if not SuggestedVolunteer.objects.filter(
                team_request=team_request,
                volunteer=volunteer
            ).exists():
                raise serializers.ValidationError("المتطوع غير مقترح لهذا الطلب")

        team_request = idea.team_requests.filter(
            status="APPROVED"
        ).order_by("-created_at").first()

        if not team_request:
            raise serializers.ValidationError("لا يوجد طلب فريق فعال")

        if idea.team_status == TeamStatus.TEAM_FULL:
            raise serializers.ValidationError("الفريق مكتمل")

        if JoinRequest.objects.filter(
            requester=user,
            volunteer=volunteer,
            idea=idea,
            status=JoinRequest.PENDING
        ).exists():
            raise serializers.ValidationError("لديك طلب انضمام قيد الانتظار")
        
        if JoinRequest.objects.filter(
            requester=user,
            volunteer=volunteer,
            idea=idea,
            status=JoinRequest.REJECTED
        ).exists():
            raise serializers.ValidationError("لا يمكنك إعادة إرسال طلب لهذا المتطوع")
        
        if not data.get("required_skill"):
            raise serializers.ValidationError("المهارة مطلوبة")

        if not data.get("tasks"):
            raise serializers.ValidationError("المهام مطلوبة")

        data["volunteer"] = volunteer
        data["idea"] = idea
        data["team_request"] = team_request

        return data

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
            "description",
            "created_at",
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
    name = serializers.CharField(source="user.full_name", read_only=True)
    avatar = serializers.SerializerMethodField()
    primary_skill = serializers.CharField(source="primary_skills", read_only=True)
    availability = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerProfile
        fields = [
            "id",
            "name",
            "avatar",
            "primary_skill",
            "availability",
        ]

    def get_avatar(self, obj):
        #  لا يوجد field  safe return
        if hasattr(obj.user, "avatar"):
            return obj.user.avatar.url if obj.user.avatar else None
        return None

    def get_availability(self, obj):
        availabilities = obj.availabilities.all()

        if not availabilities:
            return None

        # حسب الفلو: "من - إلى"
        first = availabilities.first()

        return {
            "day": first.day,
            "from": first.start_time,
            "to": first.end_time
        }