from datetime import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.events import EventBus
from evaluations.models import EvaluationAssignment
from ideas.models import IdeaStatus


@transaction.atomic
def schedule_meeting(*, idea, date, time, actor=None):

    # 1. validate input
    if not date or not time:
        raise ValidationError("يجب تحديد التاريخ والوقت")

    # 2. build datetime
    meeting_datetime = timezone.make_aware(
        datetime.combine(date, time),
        timezone.get_current_timezone()
    )

    # 3. prevent past meetings
    if meeting_datetime <= timezone.now():
        raise ValidationError("لا يمكن تحديد موعد في الماضي")

    # 4. validate idea status
    if idea.status != IdeaStatus.EVALUATION:
        raise ValidationError(
            "لا يمكن تحديد موعد لهذه الفكرة في حالتها الحالية"
        )

    # 5. get assignments
    assignments = EvaluationAssignment.objects.select_related(
        "evaluator",
        "idea"
    ).filter(
        idea=idea
    )

    if not assignments.exists():
        raise ValidationError("لا يوجد مقيمون معينون")

    # 6. already scheduled
    if assignments.filter(meeting_date__isnull=False).exists():
        raise ValidationError(
            "تم تحديد موعد لهذه الفكرة مسبقًا"
        )

    # 7. prevent same-hour meetings
    if EvaluationAssignment.objects.filter(
        meeting_date__date=meeting_datetime.date(),
        meeting_date__hour=meeting_datetime.hour
    ).exists():
        raise ValidationError(
            "يوجد جلسة تقييم أخرى بنفس الساعة"
        )

    assignments_list = list(assignments)

    # 8. update meeting
    assignments.update(
        meeting_date=meeting_datetime
    )

    # 9. emit event
    EventBus.emit(
        "evaluation_meeting_scheduled",
        idea=idea,
        assignments=assignments_list,
        meeting_datetime=meeting_datetime,
        actor=actor
    )

    return True