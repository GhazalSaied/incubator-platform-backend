from bootcamp.models import BootcampAttendance, BootcampDecision
from ideas.models import Idea, IdeaStatus
from ideas.services.state.idea_state_service import IdeaStateService
from notifications.models import Notification
from ideas.phases import SeasonPhase
from ideas.services.season_phase_service import SeasonPhaseService
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from admin_panel.bootcamp.attendance.services import calculate_absence
from django.db import transaction
from core.events import EventBus
from django.db.models import Count, Q
from bootcamp.models import BootcampDecision
from admin_panel.bootcamp.attendance.services import calculate_absence

#\\\\\\\\ideas list\\\\\

class BootcampIdeaQueryService:

    @staticmethod
    def list_bootcamp_ideas(search=None):
        qs = Idea.objects.filter(
            status=IdeaStatus.BOOTCAMP
        ).select_related("owner")
        
        #  Search
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(owner__full_name__icontains=search)
            )

        attendances = BootcampAttendance.objects.filter(
            idea__in=qs
        ).values("idea").annotate(
            total=Count("id"),
            absent=Count("id", filter=Q(status="absent"))
        )

        attendance_map = {
            item["idea"]: item for item in attendances
        }

        result = []
        
        for idea in qs:
            stats = attendance_map.get(idea.id, {})

            total = stats.get("total", 0)
            absent = stats.get("absent", 0)

            absence_percentage = (absent / total * 100) if total > 0 else 0
            commitment = 100 - absence_percentage
            
            result.append({
                "idea_id": idea.id,
                "idea_title": idea.title,
                
                "absence_percentage": f"{int(absence_percentage)}%",
                "commitment_status": "ملتزم" if commitment >= 75 else "غير ملتزم"
            })

        return result
    
    
    

#\\\\decision logic\\\\\\

def check_all_attendance_submitted(idea):
    pending = BootcampAttendance.objects.filter(
        idea=idea,
        is_submitted=False
    ).exists()

    if pending:
        raise ValidationError({
            "detail": "لا يمكن اتخاذ قرار قبل إرسال جميع سجلات الحضور."
        })
@transaction.atomic
def process_bootcamp_decision(*, idea_id, decision, actor=None):

    idea = get_object_or_404(Idea, id=idea_id)

    check_all_attendance_submitted(idea)

    if hasattr(idea, "bootcamp_decision"):
        raise ValidationError({
            "detail": "تم اتخاذ القرار مسبقاً لهذه الفكرة."
        })

    if decision == "approve":
        new_status = IdeaStatus.EVALUATION
        decision_value = "accepted"

    elif decision == "reject":
        new_status = IdeaStatus.BOOTCAMP_FAILED
        decision_value = "rejected"

    else:
        raise ValidationError({
            "detail": "القرار المرسل غير صالح."
        })

    total, absent, absence_percentage = calculate_absence(idea)
    attendance_rate = 100 - absence_percentage

    BootcampDecision.objects.update_or_create(
        idea=idea,
        defaults={
            "attendance_rate": round(attendance_rate, 2),
            "decision": decision_value,
        }
    )

    IdeaStateService.change_status(
        idea=idea,
        to_status=new_status,
        user=actor,
        source="bootcamp_decision"
    )

    EventBus.emit(
        "bootcamp_decision_made",
        idea=idea,
        decision=decision_value,
        actor=actor
    )

    return idea



#\\\\\\\\\\\\\\\\\\\\\\\\\\اعلان انتهاء جلسات المعسكر \\\\\\\\\\\\\\\\\\\\\

@transaction.atomic
def end_bootcamp_sessions(season, actor=None):

    # 1. جلب كل أفكار المعسكر
    ideas = Idea.objects.filter(
        season=season,
        status=IdeaStatus.BOOTCAMP
    ).select_related("owner")

    if not ideas.exists():
        raise ValidationError({
            "ideas": "لا يوجد أفكار في المعسكر"
        })

    EventBus.emit("bootcamp_sessions_ended",season_id=season.id,idea_ids=list(ideas.values_list("id", flat=True)),actor_id=actor.id if actor else None)

    return True