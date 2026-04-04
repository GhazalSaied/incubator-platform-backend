from ideas.models import Idea


def get_admin_ideas(request):
    season_id = request.query_params.get("season")

    queryset = Idea.objects.select_related("season").order_by("-created_at")

    if season_id:
        if not season_id.isdigit():
            raise ValueError("season must be a number")

        queryset = queryset.filter(season_id=season_id)

    return queryset

def get_idea_detail_queryset():
    return Idea.objects.all()