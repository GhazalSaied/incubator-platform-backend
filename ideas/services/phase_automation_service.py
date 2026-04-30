from ideas.models import Idea, IdeaStatus
from ideas.phases import SeasonPhase
from ideas.services.state.idea_state_service import (
    IdeaStateService
)


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