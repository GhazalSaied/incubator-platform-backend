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
    if not SeasonPhaseService.is_phase(SeasonPhase.BOOTCAMP):
        raise ValidationError("هذه الصفحة متاحة فقط خلال مرحلة المعسكر")

    ideas = Idea.objects.filter(
        bootcamp_status__in=["pending", "accepted"]
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
            "commitment_status": "ملتزم" if commitment >= 70 else "غير ملتزم",
            "bootcamp_status": idea.bootcamp_status
        })

    return result

#\\\\decision logic\\\\\\
def process_bootcamp_decision(idea_id, decision, message):
    idea = get_object_or_404(Idea, id=idea_id)

    if not SeasonPhaseService.is_phase(SeasonPhase.BOOTCAMP):
        raise ValidationError("ليس وقت اتخاذ القرار")

    if idea.status != IdeaStatus.UNDER_REVIEW:
        raise ValidationError("الفكرة ليست ضمن المعسكر")

    if idea.bootcamp_status != "pending":
        raise ValidationError("تم اتخاذ قرار مسبقاً")

    if decision == "approve":
        idea.bootcamp_status = "accepted"

    elif decision == "reject":
        idea.bootcamp_status = "rejected"
        idea.status = IdeaStatus.REJECTED

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