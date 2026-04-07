from bootcamp.models import BootcampAttendance
from ideas.models import Idea, IdeaStatus
from notifications.models import Notification
from ideas.phases import SeasonPhase
from ideas.services.season_phase_service import SeasonPhaseService
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

def calculate_absence(idea):
    total = BootcampAttendance.objects.filter(idea=idea).count()
    absent = BootcampAttendance.objects.filter(
        idea=idea,
        status="absent"
    ).count()

    percentage = (absent / total * 100) if total > 0 else 0
    return percentage

#\\\\\\\\ideas list\\\\\
def get_bootcamp_ideas(search=None):
    ideas = Idea.objects.filter(
        status__in=[
            IdeaStatus.BOOTCAMP,
        ]
    )

    if search:
        ideas = ideas.filter(title__icontains=search)

    result = []

    for idea in ideas:
        absence = calculate_absence(idea)
        commitment = 100 - absence

        result.append({
            "idea_id": idea.id,
            "idea_title": idea.title,
            "absence_percentage": round(absence, 2),
            "commitment_status": "ملتزم" if commitment >= 70 else "غير ملتزم"
        })

    return result

#\\\\decision logic\\\\\\
def process_bootcamp_decision(idea_id, decision, message):
    idea = get_object_or_404(Idea, id=idea_id)

    if not SeasonPhaseService.is_phase(SeasonPhase.BOOTCAMP):
        raise ValidationError("ليس وقت اتخاذ القرار")

    if idea.status != IdeaStatus.BOOTCAMP:
        raise ValidationError("الفكرة ليست ضمن المعسكر")

    if idea.status =="PRE_ACCEPTED" or idea.status == "REJECTED":
        raise ValidationError("تم اتخاذ قرار مسبقاً")

    if decision == "approve":
        idea.status = "PRE_ACCEPTED"

    elif decision == "reject":
        idea.status = "REJECTED"
        

    else:
        raise ValidationError("قرار غير صالح")

    idea.decision_note = message
    idea.save()

    Notification.objects.create(
        user=idea.owner,
        title="قرار المعسكر",
        message=message
    )

    return idea