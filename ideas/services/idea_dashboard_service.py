from django.utils.timezone import now
from ideas.models import Idea, IdeaStatus
from bootcamp.models import BootcampSession
from admin_panel.bootcamp.attendance.services import calculate_absence
from django.utils.timezone import now
from bootcamp.models import BootcampSession, BootcampAttendance


class IdeaDashboardService:

    @staticmethod
    def build(user):

        idea = Idea.objects.filter(owner=user).order_by("-created_at").first()

        if not idea:
            return {"detail": "لا يوجد فكرة"}

        STATUS_TO_PHASE = {
            IdeaStatus.SUBMITTED: "SUBMISSION",
            IdeaStatus.BOOTCAMP: "BOOTCAMP",
            IdeaStatus.EVALUATION: "EVALUATION",
            IdeaStatus.INCUBATION: "INCUBATION",
            IdeaStatus.EXHIBITION: "EXHIBITION",
        }

        phase = STATUS_TO_PHASE.get(idea.status, "SUBMISSION")

        progress = ["SUBMISSION", "BOOTCAMP", "EVALUATION", "INCUBATION", "EXHIBITION"]

        handler_map = {
            "SUBMISSION": IdeaDashboardService._submission,
            "BOOTCAMP": IdeaDashboardService._bootcamp,
            "EVALUATION": IdeaDashboardService._evaluation,
            "INCUBATION": IdeaDashboardService._incubation,
            "EXHIBITION": IdeaDashboardService._exhibition,
        }

        handler = handler_map.get(phase)

        return {
            "phase": phase,
            "progress": progress,
            "data": handler(idea) if handler else {}
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
            phase__phase="BOOTCAMP",
            is_active=True
        ).order_by("start_time")

        next_session = sessions.filter(
            start_time__gte=now()
        ).first()

        #  حساب الحضور
    
        total_sessions = BootcampAttendance.objects.filter(
            idea=idea
        ).count()

        absent_sessions = BootcampAttendance.objects.filter(
            idea=idea,
            status="absent"
        ).count()

        absence_percentage = (
            (absent_sessions / total_sessions) * 100
            if total_sessions > 0 else 0
        )

        attendance_percentage = 100 - absence_percentage


        #  كرت الجلسة القادمة

        next_session_data = None

        if next_session:
            next_session_data = {
                "phase_label": "المرحلة الأولى - المعسكر",
                "title": next_session.title,
                "date": next_session.date,
                "time": (
                    f"{next_session.start_time.strftime('%H:%M')} - "
                    f"{next_session.end_time.strftime('%H:%M')}"
                    if next_session.start_time and next_session.end_time else None
                ),
                "location": next_session.location,
                "description": next_session.tasks
            }

        #  جدول الجلسات

        sessions_data = []

        for s in sessions:
            sessions_data.append({
                "title": s.title,
                "date": s.date,
                "time": (
                    f"{s.start_time.strftime('%H:%M')} - "
                    f"{s.end_time.strftime('%H:%M')}"
                    if s.start_time and s.end_time else None
                ),
                "trainer": getattr(s.trainer, "full_name", None),
                "tasks": s.tasks,
                "status": "منتهية" if s.end_time and s.end_time < now() else "قادمة"
            })

        #  النتيجة النهائية

        return {
            "attendance_required": 75,

            #  الإحصائيات ( للفرونت)
            "attendance_stats": {
                "total_sessions": total_sessions,
                "absent_sessions": absent_sessions,
                "absence_percentage": round(absence_percentage, 2),
                "attendance_percentage": round(attendance_percentage, 2),
            },

            #  تحذير في حال الخطر
            "warning": (
                "⚠️ نسبة حضورك أقل من المطلوب (75%)"
                if attendance_percentage < 75 else None
            ),

            "next_session": next_session_data,
            "sessions": sessions_data,

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