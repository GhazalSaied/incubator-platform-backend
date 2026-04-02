from django.utils import timezone
from django.db import models
from ideas.models import Season
from ideas.phases import SeasonPhase



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


    @staticmethod
    def get_phase_permissions():
 
        phase = SeasonPhaseService.get_current_phase()

        if not phase:
            return {
                "phase": None,
                "can_submit_ideas": False,
                "can_edit_ideas": False,
                "can_withdraw_ideas": False,
                "can_evaluate": False,
            }

        return {
            "phase": phase.phase,
            "can_submit_ideas": phase.phase == SeasonPhase.SUBMISSION,
            "can_edit_ideas": phase.phase == SeasonPhase.SUBMISSION,
            "can_withdraw_ideas": phase.phase == SeasonPhase.SUBMISSION,
            "can_evaluate": phase.phase == SeasonPhase.EVALUATION,
        }