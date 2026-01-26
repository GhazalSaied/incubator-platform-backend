from django.utils import timezone
from ideas.models import Season, SeasonPhase


class SeasonPhaseService:

    @staticmethod
    def get_current_season():
        now = timezone.now().date()
        return Season.objects.filter(
            start_date__lte=now,
            end_date__gte=now
        ).first()

    @staticmethod
    def get_current_phase(season=None):
        if not season:
            season = SeasonPhaseService.get_current_season()

        if not season:
            return None

        now = timezone.now()
        return SeasonPhase.objects.filter(
            season=season,
            start_date__lte=now,
            end_date__gte=now
        ).first()

    @staticmethod
    def is_phase(season_phase_code):
        phase = SeasonPhaseService.get_current_phase()
        return phase and phase.phase == season_phase_code
