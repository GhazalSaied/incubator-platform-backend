from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from evaluations.models import EvaluationAssignment
from ideas.models import IdeaStatus
from admin_panel.evaluations.events import on_meeting_scheduled


@transaction.atomic
def schedule_meeting(*, idea, date, time):

    if not date or not time:
        raise ValidationError("يجب تحديد التاريخ والوقت")

    meeting_datetime = timezone.make_aware(
        timezone.datetime.combine(date, time),
        timezone.get_current_timezone()
    )

    if meeting_datetime <= timezone.now():
        raise ValidationError("لا يمكن تحديد موعد في الماضي")

    if idea.status != IdeaStatus.PRE_ACCEPTED:
        raise ValidationError("لا يمكن تحديد موعد لهذه الفكرة في حالتها الحالية")

    assignments = EvaluationAssignment.objects.filter(idea=idea)

    if not assignments.exists():
        raise ValidationError("لا يوجد مقيمون معينون")

    if assignments.filter(meeting_date__isnull=False).exists():
        raise ValidationError("تم تحديد موعد لهذه الفكرة مسبقًا")

    # 🔥 الحل تبعك
    if EvaluationAssignment.objects.filter(
        meeting_date=meeting_datetime
    ).exists():
        raise ValidationError("يوجد جلسة تقييم أخرى بنفس الوقت")

    assignments.update(meeting_date=meeting_datetime)

    idea.status = IdeaStatus.EVALUATION
    idea.save(update_fields=["status"])

    on_meeting_scheduled(
        idea=idea,
        meeting_datetime=meeting_datetime,
        assignments=assignments
    )