from django.utils.timezone import now
from ideas.models import Idea, IdeaStatus
from bootcamp.models import BootcampSession
from django.utils.timezone import now
from bootcamp.models import BootcampSession, BootcampAttendance
from ideas.services.idea_service import IdeaService
from bootcamp.services.attendance_service import AttendanceService
from evaluations.models import EvaluationAssignment ,Evaluation
from ideas.models import ExhibitionForm
from evaluations.serializers import IncubationReviewSerializer

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

        if idea.status not in STATUS_TO_PHASE:
            raise ValueError(f"Unsupported status: {idea.status}")

        phase = STATUS_TO_PHASE[idea.status]

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
    def _bootcamp(idea,user):
        
        idea = IdeaService.get_user_idea(user)
        sessions = BootcampSession.objects.filter(
            phase__season=idea.season,
            phase__phase="BOOTCAMP",
            is_active=True
        ).order_by("start_time")

        next_session = sessions.filter(
            start_time__gte=now()
        ).first()

       
        
        #  حساب الحضور
        attendance = AttendanceService.get_stats(idea)
         
        #  كرت الجلسة القادمة
        
        next_session_data = None

        if next_session:
            next_session_data = {
                "id": next_session.id,
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
                "id": s.id,
                "title": s.title,
                "date": s.date,
                "time": (
                    f"{s.start_time.strftime('%H:%M')} - "
                    f"{s.end_time.strftime('%H:%M')}"
                    if s.start_time and s.end_time else None
                ),
                "trainer": (
                    s.trainer.full_name
                    if s.trainer and hasattr(s.trainer, "full_name")
                    else str(s.trainer) if s.trainer else None
                ),
                "tasks": s.tasks,
                "status": "منتهية" if s.end_time and s.end_time < now() else "قادمة"
            })

        return {
            "attendance": attendance,
            "next_session": next_session_data,
            "sessions": sessions_data
        }

        


    @staticmethod
    def _evaluation(idea):

        assignment = EvaluationAssignment.objects.filter(
            idea=idea
        ).first()

        result = Evaluation.objects.filter(
            idea=idea,
            is_submitted=True
        ).first()

        # تحديد الحالة
        if not assignment:
            status = "pending"
        elif assignment and not result:
            status = "in_review"
        else:
            status = "completed"

        return {
            "status": status,
            "meeting_date": getattr(assignment, "meeting_date", None),
            "notes": getattr(result, "notes", None),
            "can_request_consultation": True
        }
    

    @staticmethod
    def _incubation(idea):
        reviews = idea.reviews.order_by("-meeting_date")[:10]
        

        return {
            "warning": "عدم تحقيق تقدم قد يؤدي لإنهاء الاحتضان",
            "next_review": (
                    IncubationReviewSerializer(reviews.first()).data
                    if reviews.exists()
                    else None
            ),
            "reviews": IncubationReviewSerializer(reviews, many=True).data,
            "can_request_consultation": True
        }



    @staticmethod
    def _exhibition(idea):

        form = getattr(idea.season, "exhibition_form", None)

        questions = []

        if form:
            for q in form.questions.order_by("order"):
                questions.append({
                    "id": q.id,
                    "key": q.key,
                    "label": q.label,
                    "type": q.type,
                    "required": q.required,
                    "options": [
                        {"value": o.value, "label": o.label}
                        for o in q.options.all().order_by("order")
                    ]
                })

        return {
            "message": "يرجى تجهيز بطاقة المشروع للمعرض",
            "form": {
                "id": getattr(form, "id", None),
                "title": getattr(form, "title", None),
                "questions": questions
            },
            "can_edit": True
        }