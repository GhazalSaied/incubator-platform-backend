from volunteers.models import (
    VolunteerProfile,
    ConsultationRequest,
    Workshop,
    WorkshopRegistration,
)
from django.utils import timezone
from messaging.models import Conversation
from notifications.services.notification_service import NotificationService
from ideas.models import TeamMember 



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

        next_workshop = get_next_workshop(user)

        return {
            "profile": profile,
            "availability": availability,
            "consultations": {
                "pending": consultations.filter(status="PENDING").count(),
                "accepted": consultations.filter(status="ACCEPTED").count(),
                "rejected": consultations.filter(status="REJECTED").count(),
            "workshop_stats": get_workshop_stats(user),
            "next_workshop": {
                "title": next_workshop.title,
                "start_date": next_workshop.start_date,
                "time_from": next_workshop.time_from
        } if next_workshop else None,
            
            }
        }
    
#/////////////////////////// CONSULTATION REQUEST ///////////////////

    @staticmethod
    def handle_consultation_decision(user, request_id, action):

        profile = VolunteerService.get_profile(user)

        consultation = ConsultationRequest.objects.get(
            id=request_id,
            volunteer=profile
        )

        if consultation.idea.team_status == "team_full":
             raise Exception("الفريق مكتمل بالفعل")
        
        if action == "accept":
            consultation.status = ConsultationRequest.ACCEPTED

            conversation, _ = Conversation.objects.get_or_create()
            conversation.participants.add(user, consultation.requester)

            NotificationService.send(
                user=consultation.requester,
                title="تم قبول طلبك",
                message="تم قبول طلبك من قبل المتطوع",
                notification_type="SUCCESS",
                related_object=consultation,
                action_url=f"/chat/{conversation.id}",
                target_role="VOLUNTEER"
            )

            if consultation.request_type == ConsultationRequest.JOIN_REQUEST:
                
                idea = consultation.idea
                team_request = consultation.team_request

                current_members = TeamMember.objects.filter(
                    idea=idea
                ).count()

                if current_members >= team_request.members_needed:
                    raise Exception("تم الوصول للعدد المطلوب من الفريق")

                TeamMember.objects.get_or_create(
                    idea=idea,
                    user=user
                )

                #  تحديث حالة الفريق
                current_members += 1

                if current_members >= team_request.members_needed:
                    idea.team_status = "team_full"
                    #  notification 
                    NotificationService.send(
                        user=idea.owner,
                        title="اكتمل فريقك 🎉",
                        message="تم اكتمال فريق مشروعك بنجاح",
                        notification_type="SUCCESS",
                        target_role="IDEA_OWNER"
                    )

                else:
                    consultation.idea.team_status = "team_building"

                    #  notification انضمام عضو جديد
                    NotificationService.send(
                        user=idea.owner,
                        title="انضمام متطوع جديد",
                        message=f"تم انضمام {user.full_name} إلى فريق مشروعك",
                        notification_type="INFO",
                        target_role="IDEA_OWNER"
                    )

                idea.save()

        else:
            consultation.status = ConsultationRequest.REJECTED

            NotificationService.send(
                user=consultation.requester,
                title="تم رفض طلبك",
                message="تم رفض طلبك من قبل المتطوع",
                notification_type="WARNING",
                related_object=consultation,
                target_role="IDEA_OWNER"
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