from ideas.models import Idea
from ideas.models import IdeaStatus
from evaluations.models import EvaluationAssignment

def get_assignment_dashboard_ideas(
    season,
    sector=None,
    target_audience=None
):
    queryset = Idea.objects.filter(
        season=season,
        status=IdeaStatus.PRE_ACCEPTED
    ).prefetch_related(
        "evaluation_assignments__evaluator"
    )

    if sector:
        queryset = queryset.filter(sector=sector)

    if target_audience:
        queryset = queryset.filter(
            target_audience=target_audience
        )

    return queryset