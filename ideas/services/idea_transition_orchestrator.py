from ideas.services.state.idea_state_service import IdeaStateService
from ideas.services.phase_trigger_service import PhaseTriggerService
from ideas.models import Idea, IdeaStatus
from ideas.phases import SeasonPhase
from ideas.services.state.idea_state_service import (
    IdeaStateService
)

class IdeaTransitionOrchestrator:

    @staticmethod
    def change_status(*, idea, to_status, user=None):

        # 🟡 STEP 1: حاول تفتح المرحلة قبل التغيير
        PhaseTriggerService.ensure_phase_allows_transition(
            idea=idea,
            to_status=to_status
        )

        # 🟢 STEP 2: نفذ التغيير (Core)
        updated_idea = IdeaStateService.change_status(
            idea=idea,
            to_status=to_status,
            user=user
        )

        # 🔵 STEP 3: تحقق إذا لازم تنتقل مرحلة بعد التغيير
        PhaseTriggerService.handle_idea_status_changed({
            "idea": updated_idea
        })

        return updated_idea
    
    



class PhaseAutomationService:

    @staticmethod
    def run(season, phase):

        # =================================
        # INCUBATION
        # =================================

        if phase == SeasonPhase.INCUBATION:

            ideas = Idea.objects.filter(
                season=season,
                status=IdeaStatus.ACCEPTED
            )

            for idea in ideas:

                try:

                    IdeaStateService.change_status(
                        idea=idea,
                        to_status=IdeaStatus.INCUBATION,
                        source="phase_automation"
                    )

                    print(
                        f"INCUBATION SUCCESS idea={idea.id}"
                    )

                except Exception as e:

                    print(
                        f"INCUBATION FAILED idea={idea.id} error={e}"
                    )

        # =================================
        # EXHIBITION
        # =================================

        elif phase == SeasonPhase.EXHIBITION:

            ideas = Idea.objects.filter(
                season=season,
                status=IdeaStatus.EXHIBITION
            )

            for idea in ideas:

                try:

                    IdeaStateService.change_status(
                        idea=idea,
                        to_status=IdeaStatus.GRADUATED_POSITIVE,
                        source="phase_automation"
                    )

                    print(
                        f"GRADUATION SUCCESS idea={idea.id}"
                    )

                except Exception as e:

                    print(
                        f"GRADUATION FAILED idea={idea.id} error={e}"
                    )