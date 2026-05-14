
from django.utils import timezone
from django.db import transaction
from core.events import EventBus
from ideas.phases import SeasonPhase 
from ideas.models import Idea, IdeaStatus
from ideas.phases import SeasonPhase as PhaseEnum
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.services.state.idea_state_service import IdeaStateService
from ideas.services.phase_automation_service import (
    PhaseAutomationService
)

class PhaseTriggerService:
    @staticmethod
    def ensure_phase_allows_transition(idea, to_status):

        current_phase = SeasonPhaseService.get_current_phase(idea.season)

        if not current_phase:
            return

        phase = current_phase.phase

    #  إذا نحن في submission ونريد PRE_ACCEPTED
        if phase == PhaseEnum.SUBMISSION and to_status == IdeaStatus.PRE_ACCEPTED:

        #  نغلق submission ونفتح bootcamp
            PhaseTriggerService._move_to_next_phase(
                idea.season,
                PhaseEnum.BOOTCAMP
            )

    @staticmethod
    def handle_idea_status_changed(payload):
        idea = payload.get("idea")

        if not idea:
            return

        season = idea.season

        current_phase = SeasonPhaseService.get_current_phase(season)

        if not current_phase:
            return

        phase = current_phase.phase

        #  Submission → Bootcamp
        if phase == PhaseEnum.SUBMISSION:
            PhaseTriggerService._check_submission_end(season)

        #  Bootcamp → Evaluation
        elif phase == PhaseEnum.BOOTCAMP:
            PhaseTriggerService._check_bootcamp_end(season)

        #  Evaluation → incubation
        elif phase == PhaseEnum.EVALUATION:
            PhaseTriggerService._check_evaluation_end(season)
        #  Incubation → Exhibition
        elif phase == PhaseEnum.INCUBATION:
            PhaseTriggerService._check_incubation_end(season)
            
    EventBus.register("idea_status_changed", handle_idea_status_changed)
    
        
    # ----------------------------------

    @staticmethod
    def _check_submission_end(season):
        # مثال شرط: لا يوجد أفكار SUBMITTED
        if not Idea.objects.filter(
            season=season,
            status=IdeaStatus.SUBMITTED
        ).exists():

            PhaseTriggerService._move_to_next_phase(
                season,
                PhaseEnum.BOOTCAMP
            )

    # ----------------------------------

    @staticmethod
    def _check_bootcamp_end(season):
        # كل الأفكار خلصت bootcamp
        remaining = Idea.objects.filter(
            season=season,
            status__in=[
                IdeaStatus.PRE_ACCEPTED,
                IdeaStatus.BOOTCAMP
            ]
        ).exists()

        if not remaining:
            PhaseTriggerService._move_to_next_phase(
                season,
                PhaseEnum.EVALUATION
            )

    # ----------------------------------
    @transaction.atomic
    @staticmethod
    def _check_evaluation_end(season):
        remaining = Idea.objects.filter(
            season=season,
            status__in=[
                IdeaStatus.EVALUATION,
                IdeaStatus.EVALUATED
            ]
        ).exists()

        if not remaining:
            PhaseTriggerService._move_to_next_phase(
                season,
                PhaseEnum.INCUBATION
            )
           
          
    @staticmethod
    def _check_incubation_end(season):
        remaining = Idea.objects.filter(
            season=season,
            status__in=[
                IdeaStatus.INCUBATION,
                IdeaStatus.ACCEPTED
            ]
        ).exists()

        if not remaining:
            PhaseTriggerService._move_to_next_phase(
                season,
                PhaseEnum.EXHIBITION
            )
           

    # ----------------------------------

    @staticmethod
    @transaction.atomic
    def _move_to_next_phase(season, next_phase):

        now = timezone.now()

        current_phase = SeasonPhaseService.get_current_phase(season)

        #  حماية من التكرار
        if not current_phase or current_phase.phase == next_phase:
            return

        #  إغلاق المرحلة الحالية
        current_phase.end_date = now
        current_phase.save(update_fields=["end_date"])

        #  إنشاء المرحلة الجديدة
        SeasonPhase.objects.create(
            season=season,
            phase=next_phase,
            start_date=now,
            end_date=None,
            order=current_phase.order + 1
        )
        print("NEW PHASE:", next_phase)
        PhaseAutomationService.run(
        season,
        next_phase
    )
      
