from volunteers.models import (
    VolunteerProfile,
    ConsultationRequest
)

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

        return {
            "profile": profile,
            "availability": availability,
            "consultations": {
                "pending": consultations.filter(status="PENDING").count(),
                "accepted": consultations.filter(status="ACCEPTED").count(),
                "rejected": consultations.filter(status="REJECTED").count(),
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
                action_url=f"/chat/{conversation.id}"
            )

            if consultation.request_type == ConsultationRequest.JOIN:
                TeamMember.objects.get_or_create(
                    idea=consultation.idea,
                    user=user
                )

        else:
            consultation.status = ConsultationRequest.REJECTED

            NotificationService.send(
                user=consultation.requester,
                title="تم رفض طلبك",
                message="تم رفض طلبك من قبل المتطوع",
                notification_type="WARNING",
                related_object=consultation
            )

        consultation.save()
        return consultation