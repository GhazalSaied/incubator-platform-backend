from admin_panel.evaluations.services.evaluation_results_service import (
    EvaluationStatusService
)

from ideas.services.state.idea_state_service import (
    IdeaStateService
)

from ideas.models import IdeaStatus


def handle_evaluation_completed(payload):

    idea = payload.get("idea")

    if not idea:
        idea = payload.get("payload", {}).get("idea")

    if not idea:
        return

    is_fully_evaluated = EvaluationStatusService.is_fully_evaluated(idea)

    if not is_fully_evaluated:
        return

    if idea.status == IdeaStatus.EVALUATED:
        return

    IdeaStateService.change_status(
        idea=idea,
        to_status=IdeaStatus.EVALUATED,
        source="evaluation_auto_complete"
    )

    