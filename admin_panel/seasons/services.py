from ideas.models import Season, Idea, IdeaStatus
from django.shortcuts import get_object_or_404


def create_season(data):
    season = Season.objects.create(**data)
    return season


def publish_season(season_id):
    season = get_object_or_404(Season, id=season_id)

    season.is_published = True
    season.save()

    return season


def close_season(season_id):
    season = get_object_or_404(Season, id=season_id)

    if not season.is_open:
        raise ValueError("الموسم مغلق بالفعل")

    season.is_open = False
    season.save()

    Idea.objects.filter(
        season=season,
        status=IdeaStatus.SUBMITTED
    ).update(status=IdeaStatus.UNDER_REVIEW)

    return season