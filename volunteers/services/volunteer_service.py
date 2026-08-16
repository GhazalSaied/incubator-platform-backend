from accounts.constants import SystemRoles
from accounts.role_service import RoleService
from volunteers.models import (
    VolunteerProfile,
    ConsultationRequest,
    Workshop,
    WorkshopRegistration,
    JoinRequest,
    VolunteerAvailability,
    PrimarySkillChoices
)
from django.utils import timezone
from core.events import EventBus
from notifications.services.notification_service import NotificationService
from ideas.models import TeamMember 
from ideas.services.team_service import TeamService
from ideas.models import TeamStatus
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch
from messaging.models import Conversation, ConversationParticipant
from messaging.domain.constants.messaging_constants import ConversationType

from messaging.domain.services.conversation_service import ConversationService
class VolunteerService:

#//////////////////// GET PROFILE /////////////////

    @staticmethod
    def get_profile(user):
        try:
            return user.volunteer_profile
        except:
            raise ValidationError("أنت لست متطوعاً")
        


#/////////////////////// DASHBOARD ///////////////
 
    @staticmethod
    def get_dashboard(user):

        profile = VolunteerService.get_profile(user)

        availability = profile.availabilities.all().order_by("day")
        consultations = profile.consultation_requests.all()

        next_workshop = VolunteerService.get_next_workshop(user)

        return {
            "profile": profile,
            "availability": availability,

            "consultations": {
                "pending": consultations.filter(status="PENDING").count(),
                "accepted": consultations.filter(status="ACCEPTED").count(),
                "rejected": consultations.filter(status="REJECTED").count(),
            },

            "workshop_stats": VolunteerService.get_workshop_stats(user),
            "next_workshop": {
                "title": next_workshop.title,
                "start_date": next_workshop.start_date,
                "time_from": next_workshop.time_from
        } if next_workshop else None,
            
        }
        
    
#/////////////////////////// CONSULTATION REQUEST ///////////////////


    @transaction.atomic
    @staticmethod
    def handle_consultation_decision(user, request_id, action):

        profile = VolunteerService.get_profile(user)

        try:
            consultation = ConsultationRequest.objects.select_for_update().get(
                id=request_id,
                volunteer=profile
            )
        except ConsultationRequest.DoesNotExist:
            raise ValidationError("الطلب غير موجود أو لا تملك صلاحية الوصول إليه")

        #   منع اتخاذ قرار مرتين
        if consultation.status != ConsultationRequest.PENDING:
            raise ValidationError("تم اتخاذ قرار مسبقاً")

        
        if action == "accept":

            consultation.status = ConsultationRequest.ACCEPTED

        # إنشاء أو جلب المحادثة بين المستشار وصاحب الطلب
            conversation = ConversationService.start_private_conversation(
            creator=user,
            target_user=consultation.requester,
        )

        # إرسال الإشعار مع المحادثة
            EventBus.emit(
            "consultation_accepted",
            consultation=consultation,
            actor=user,
            conversation=conversation,
        )
        else:
            consultation.status = ConsultationRequest.REJECTED
            
            EventBus.emit(
                "consultation_rejected",
                consultation=consultation,
                actor=user
            )
        consultation.save()
        return consultation

    #//////////////////////// HANDLE JOIN REQUESTS //////////////////////////

    @transaction.atomic
    @staticmethod
    def handle_join_request_decision(user, request_id, action):

        profile = VolunteerService.get_profile(user)

        join_request = JoinRequest.objects.get(
            id=request_id,
            volunteer=profile
        )

        if join_request.status != JoinRequest.PENDING:
            raise ValidationError("تم اتخاذ قرار مسبقاً")

        idea = join_request.idea
        team_request = join_request.team_request

        if action == "accept":

            TeamService.add_member(
                idea=idea,
                user=user,
                team_request=team_request
            )

            join_request.status = JoinRequest.ACCEPTED
            join_request.save(update_fields=["status"])
            RoleService.assign_role(
                user=user,
                role_code=SystemRoles.INCUBATOR 
            )

            EventBus.emit(
                "join_request_accepted",
                join_request=join_request,
                actor=user
            )
        else:
            join_request.status = JoinRequest.REJECTED

           
            EventBus.emit (

            "join_request_rejected",
            join_request=join_request,  
            actor=user
            )

            

        join_request.save()
        return join_request
    

    #////////////////// WORKSHOP STATS > عدد كل الورشات بمختلف حالاتها //////////

    @staticmethod
    def get_workshop_stats(user):
        workshops = Workshop.objects.filter(created_by=user)

        return {
            "total": workshops.count(),
            "accepted": workshops.filter(status="ACCEPTED").count(),
            "pending": workshops.filter(status="PENDING").count(),
            "rejected": workshops.filter(status="REJECTED").count(),
        }

    #//////////////////// NEXT WORKSHOP > اقرب ورشة عمل  ///////////
    
    @staticmethod
    def get_next_workshop(user):
        return Workshop.objects.filter(
            created_by=user,
            status="ACCEPTED",
            start_date__gte=timezone.now().date()
        ).order_by("start_date").first()
    

    #///////////////////// GET CONSULTANTS BY PRIMARY SKILL //////////////////////

    @staticmethod
    def get_consultants_by_primary_skill(primary_skill):
        valid_skills = {
            choice[0]
            for choice in PrimarySkillChoices.choices
        }

        if primary_skill not in valid_skills:
            return VolunteerProfile.objects.none()

        return (
            VolunteerProfile.objects
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "availabilities",
                    queryset=VolunteerAvailability.objects.all()
                )
            )
            .filter(
                status=VolunteerProfile.APPROVED,
                primary_skills=primary_skill
            )
            .order_by("-created_at")
        )