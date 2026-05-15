from django.utils import timezone
from django.db import models
from ideas.models import Season
from ideas.phases import SeasonPhase




from django.utils import timezone
from ideas.models import Season, SeasonStatus


from django.utils import timezone


class SeasonPhaseService:

    @staticmethod
    def get_current_season():

        now = timezone.now()

        current_phase = SeasonPhase.objects.filter(
            start_date__lte=now
        ).filter(
            models.Q(end_date__isnull=True) |
            models.Q(end_date__gte=now)
        ).select_related("season").order_by("-order").first()

        if not current_phase:
            return None

        if current_phase.season.status == SeasonStatus.DRAFT:
            return None

        return current_phase.season
        
 
    @staticmethod
    def get_current_phase(season=None):

        if not season:
            season = SeasonPhaseService.get_current_season()
            print("Current season:", season)
        if not season:
            return None

        now = timezone.now()

        return SeasonPhase.objects.filter(
            season=season,
            start_date__lte=now
        ).filter(
            models.Q(end_date__isnull=True) |
            models.Q(end_date__gte=now)
        ).order_by("-order").first()


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
                "can_add_sessions": False,
                "can_decide_end_of_bootcamp_sessions": False,
                "can_make_bootcamp_decisions": False,
                "can_evaluate": False,
                "can_assign_evaluators": False,
                "can_schedule_meetings": False,
                "can_decide_final_results": False,
                "can_assign_mentors": False,
                "can_remove_mentors": False,
                "can_schedule_incubation_meetings": False,
                "can_graduate_from_incubation": False,
                "can_create_exhibition": False,
                "can_decide_exhibition_card" : False,
                
            }

        return {
            "phase": phase.phase,
            "can_submit_ideas": phase.phase == SeasonPhase.SUBMISSION,
            "can_add_sessions": phase.phase == SeasonPhase.BOOTCAMP,
            "can_decide_end_of_bootcamp_sessions": phase.phase == SeasonPhase.BOOTCAMP,
            "can_make_bootcamp_decisions": phase.phase == SeasonPhase.BOOTCAMP,
            "can_evaluate": phase.phase == SeasonPhase.EVALUATION,
            "can_assign_evaluators": phase.phase == SeasonPhase.EVALUATION,
            "can_schedule_meetings": phase.phase == SeasonPhase.EVALUATION,
            "can_decide_final_results": phase.phase == SeasonPhase.EVALUATION,
            "can_assign_mentors": phase.phase == SeasonPhase.INCUBATION,
            "can_remove_mentors": phase.phase == SeasonPhase.INCUBATION,
            "can_schedule_incubation_meetings": phase.phase == SeasonPhase.INCUBATION,
            "can_graduate_from_incubation": phase.phase == SeasonPhase.INCUBATION,
            "can_create_exhibition": phase.phase == SeasonPhase.EXHIBITION,
            "can_decide_exhibition_card" : phase.phase == SeasonPhase.EXHIBITION,
        }