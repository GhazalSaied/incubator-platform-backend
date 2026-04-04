from django.utils.timezone import now
from ideas.models import Idea, IdeaStatus
from ideas.services.season_phase_service import SeasonPhaseService
from bootcamp.models import BootcampSession


class IdeaDashboardService:

    @staticmethod
    def build(user):

        try:
            idea = Idea.objects.get(owner=user)
        except Idea.DoesNotExist:
            return {"detail": "لا يوجد فكرة"}

        phase_obj = SeasonPhaseService.get_current_phase()
        phase = phase_obj.phase if phase_obj else "SUBMISSION"

        progress = ["SUBMISSION", "BOOTCAMP", "EVALUATION", "INCUBATION", "EXHIBITION"]

        handler_map = {
            "SUBMISSION": IdeaDashboardService._submission,
            "BOOTCAMP": IdeaDashboardService._bootcamp,
            "EVALUATION": IdeaDashboardService._evaluation,
            "EXHIBITION": IdeaDashboardService._exhibition,
        }

        # incubation based on status (مش phase فقط)
        if idea.status == IdeaStatus.INCUBATED:
            data = IdeaDashboardService._incubation(idea)
            return {
                "phase": "INCUBATION",
                "progress": progress,
                "data": data
            }

        handler = handler_map.get(phase)

        if not handler:
            return {
                "phase": phase,
                "progress": progress,
                "data": {}
            }

        return {
            "phase": phase,
            "progress": progress,
            "data": handler(idea)
        }

    # ---------------------

    @staticmethod
    def _submission(idea):
        return {
            "message": "تم إرسال فكرتك، بانتظار بدء المعسكر"
        }

    @staticmethod
    def _bootcamp(idea):
        sessions = BootcampSession.objects.filter(
            phase__phase="BOOTCAMP"
        ).order_by("start_time")

        next_session = sessions.filter(
            start_time__gte=now()
        ).first()

        from bootcamp.serializers import BootcampSessionSerializer

        return {
            "attendance_required": 75,
            "next_session": BootcampSessionSerializer(next_session).data if next_session else None,
            "sessions": BootcampSessionSerializer(sessions, many=True).data,
            "can_request_absence": True
        }

    @staticmethod
    def _evaluation(idea):
        return {
            "status": "بانتظار التقييم",
            "meeting_date": None,
            "notes": None,
            "can_request_consultation": True
        }

    @staticmethod
    def _incubation(idea):
        reviews = idea.reviews.order_by("-meeting_date")
        from evaluations.serializers import IncubationReviewSerializer

        return {
            "warning": "عدم تحقيق تقدم قد يؤدي لإنهاء الاحتضان",
            "next_review": IncubationReviewSerializer(reviews.first()).data if reviews else None,
            "reviews": IncubationReviewSerializer(reviews, many=True).data,
            "can_request_consultation": True
        }

    @staticmethod
    def _exhibition(idea):
        return {
            "message": "يرجى تجهيز بطاقة المشروع للمعرض",
            "can_edit": True
        }