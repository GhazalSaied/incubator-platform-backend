

from ideas.models import Idea, IdeaStatus



def get_ideas_with_evaluators(
    season,
    sector=None,
    target_audience=None
):
    queryset = Idea.objects.filter(
        season=season,
        status=IdeaStatus.PRE_ACCEPTED,
        evaluation_assignments__isnull=False
    ).distinct().prefetch_related(
        "evaluation_assignments__evaluator"
    )

    if sector:
        queryset = queryset.filter(sector=sector)

    if target_audience:
        queryset = queryset.filter(
            target_audience=target_audience
        )

    return queryset

#\\\\\\\\\\\\\\\\\\\\\get_idea_evaluators\\\\\\\\\\\\\\\\\\\\
def get_idea_evaluators(idea):

    return idea.evaluation_assignments.select_related(
        "evaluator"
    )