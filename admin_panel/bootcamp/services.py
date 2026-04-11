from django.core.exceptions import ValidationError
from ideas.phases import SeasonPhase, get_current_phase
from admin_panel.evaluations.events import on_camp_ended
from django.utils import timezone


class SeasonManagementService:

    @staticmethod
    def end_camp_and_start_evaluation(*, season):

        current_phase = get_current_phase(season)

        if not current_phase:
            raise ValidationError("لا توجد مرحلة حالية")

        if current_phase.phase != SeasonPhase.BOOTCAMP:
            raise ValidationError("العملية غير مسموحة في هذه المرحلة")

        # 🟢 إنهاء المعسكر (نعدّل end_date)
        current_phase.end_date = timezone.now()
        current_phase.save(update_fields=["end_date"])

        # 🟢 نبدأ مرحلة التقييم
        next_phase = SeasonPhase.objects.filter(
            season=season,
            phase=SeasonPhase.EVALUATION
        ).first()

        if not next_phase:
            raise ValidationError("مرحلة التقييم غير موجودة")

        next_phase.start_date = timezone.now()
        next_phase.save(update_fields=["start_date"])

        # 🟢 event
        on_camp_ended(season=season)

        return season