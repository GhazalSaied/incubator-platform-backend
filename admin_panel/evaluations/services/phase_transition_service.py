from django.utils import timezone
from ideas.models import IdeaStatus
from ideas.phases import SeasonPhase, get_current_phase



class PhaseTransitionService:

    @staticmethod
    def try_move_to_incubation(season):
        """
        🟢 Trigger ذكي:
        بيتأكد إذا في أفكار لسا بدون قرار
        """

        # 🟢 لازم نكون بمرحلة التقييم
        current_phase = get_current_phase(season)

        if not current_phase or current_phase.phase != SeasonPhase.EVALUATION:
            return False

        # 🟢 كم فكرة لسا بدون قرار؟
        remaining = season.ideas.filter(
            status=IdeaStatus.EVALUATION
        ).count()

        if remaining > 0:
            return False

        # 🟢 في أفكار مقبولة؟
        accepted_exists = season.ideas.filter(
            status=IdeaStatus.ACCEPTED
        ).exists()

        if not accepted_exists:
            return False

        # 🔥 الانتقال
        PhaseTransitionService._move_to_incubation(season)

        return True

    # ---------------------------------------------

    @staticmethod
    def _move_to_incubation(season):
        """
        🔥 تنفيذ الانتقال الفعلي
        """

        now = timezone.now()

        current_phase = get_current_phase(season)

        if not current_phase:
            return

        # 🟢 إنهاء مرحلة التقييم
        current_phase.end_date = now
        current_phase.save(update_fields=["end_date"])

        # 🟢 بدء مرحلة الاحتضان
        try:
            next_phase = SeasonPhase.objects.get(
                season=season,
                phase=SeasonPhase.INCUBATION
            )
        except SeasonPhase.DoesNotExist:
            raise Exception("مرحلة الاحتضان غير موجودة")

        next_phase.start_date = now
        next_phase.save(update_fields=["start_date"])

        # 🟢 تحديث حالة الأفكار المقبولة فقط
        season.ideas.filter(
            status=IdeaStatus.ACCEPTED
        ).update(status=IdeaStatus.INCUBATION)

        