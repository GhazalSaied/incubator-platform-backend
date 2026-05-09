from bootcamp.models import BootcampAttendance,BootcampDecision
from ideas.models import Idea, IdeaStatus
from django.db.models import Q


#\\\\\\\\حساب الغياب\\\\\\\\
def calculate_absence(idea):
    total = BootcampAttendance.objects.filter(idea=idea).count()

    absent = BootcampAttendance.objects.filter(
        idea=idea,
        status="absent"
    ).count()

    percentage = (absent / total * 100) if total > 0 else 0

    return total, absent, percentage

#\\\\\attendance list\\\\\\
def get_session_attendance(session_id):
    return BootcampAttendance.objects.filter(session_id=session_id).select_related("idea")

#\\\\\stats\\\\
def get_idea_stats(idea_id):
    idea = Idea.objects.get(id=idea_id)
    total, absent, percentage = calculate_absence(idea)

    return {
        "total_sessions": total,
        "absent_sessions": absent,
        "absence_percentage": percentage
    }
    
#\\\\\\\\participants\\\\\

class BootcampDecisionQueryService:

    @staticmethod
    def list_decisions(search=None):
        qs = BootcampDecision.objects.select_related(
            "idea",
            "idea__owner"
        )

        #  search
        if search:
            qs = qs.filter(
                Q(idea__title__icontains=search) |
                Q(idea__owner__full_name__icontains=search)
            )

        results = []

        for decision in qs:
            idea = decision.idea
            owner = idea.owner

            results.append({
                "idea_id": idea.id,
                "idea_title": idea.title,
                "owner_name": getattr(owner, "full_name", None),
                "decision": "مقبول" if decision.decision == "accepted" else "مرفوض",
                "attendance_rate": decision.attendance_rate
            })

        #  count المقبولين
        accepted_count = qs.filter(decision="accepted").count()

        return {
            "results": results,
            "accepted_count": accepted_count
        }