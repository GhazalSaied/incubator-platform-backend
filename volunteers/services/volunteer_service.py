from volunteers.models import (
    VolunteerProfile,
    ConsultationRequest,
    Workshop,
    WorkshopRegistration,
)
from django.utils import timezone
from core.events import EventBus
from messaging.models import Conversation
from notifications.services.notification_service import NotificationService
from ideas.models import TeamMember 
from ideas.services.team_service import TeamService
from ideas.models import TeamStatus



class VolunteerService:

#//////////////////// GET PROFILE /////////////////

    @staticmethod
    def get_profile(user):
        try:
            return user.volunteer_profile
        except:
            raise ValueError("أنت لست متطوعاً")

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

            "workshop_stats": get_workshop_stats(user),
            "next_workshop": {
                "title": next_workshop.title,
                "start_date": next_workshop.start_date,
                "time_from": next_workshop.time_from
        } if next_workshop else None,
            
        }
        
    
#/////////////////////////// CONSULTATION REQUEST ///////////////////

    @staticmethod
    def handle_consultation_decision(user, request_id, action):

        profile = VolunteerService.get_profile(user)

        consultation = ConsultationRequest.objects.get(
            id=request_id,
            volunteer=profile
        )

        idea = consultation.idea

        if consultation.idea.team_status == TeamStatus.TEAM_FULL:
             raise Exception("الفريق مكتمل بالفعل")
        
        if action == "accept":

            consultation.status = ConsultationRequest.ACCEPTED


            conversation, _ = Conversation.objects.get_or_create()
            conversation.participants.add(user, consultation.requester)

            # اشعار من المتطوع لصاحب الفكرة بدون فريق 
            EventBus.emit(
                "volunteer_joined_team",
                payload={
                "idea": idea,
                "volunteer": user,
                "owner": idea.owner ,
            },
             actor=user,
            )

            if consultation.request_type == ConsultationRequest.JOIN_REQUEST:
                
                team_request = consultation.team_request

                current_members = TeamMember.objects.filter(
                    idea=idea
                ).count()

                if current_members >= team_request.members_needed:
                    raise Exception("تم الوصول للعدد المطلوب من الفريق")



                TeamService.add_member(
                    idea=idea,
                    user=user,
                    team_request=team_request
                )

                if current_members >= team_request.members_needed:
                    idea.team_status = TeamStatus.TEAM_FULL
                    #  notification 
                    EventBus.emit(
                        "team_completed",
                        payload={
                            "idea": idea,
                        },
                        actor=user,
                    )

                else:
                    consultation.idea.team_status = TeamStatus.TEAM_BUILDING

                    #  notification انضمام عضو جديد
                    EventBus.emit(
                        "team_member_joined",
                        payload={
                            "idea": idea,
                            "member": user,
                        },
                        actor=user,
                    )

                idea.save()

        else:
            consultation.status = ConsultationRequest.REJECTED

            EventBus.emit(
                "join_request_rejected",
                payload={
                "idea": consultation.idea,
                "volunteer": user,
                "requester": consultation.requester,
            },
            actor=user,
            )

        consultation.save()
        return consultation


#////////////////// WORKSHOP STATS > عدد كل الورشات بمختلف حالاتها //////////

def get_workshop_stats(user):
    workshops = Workshop.objects.filter(created_by=user)

    return {
        "total": workshops.count(),
        "accepted": workshops.filter(status="ACCEPTED").count(),
        "pending": workshops.filter(status="PENDING").count(),
        "rejected": workshops.filter(status="REJECTED").count(),
    }

#//////////////////// NEXT WORKSHOP > اقرب ورشة عمل  ///////////

def get_next_workshop(user):
    return Workshop.objects.filter(
        created_by=user,
        status="ACCEPTED",
        start_date__gte=timezone.now().date()
    ).order_by("start_date").first()