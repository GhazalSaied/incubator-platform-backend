from evaluations.models import EvaluationInvitation
from volunteers.models import VolunteerProfile
from django.db.models import Q

def get_available_season_evaluators(
    season,
    specialization=None,
    skills=None,
):
    """
    Returns accepted evaluators for current season
    with optional filtering by specialization and skills
    """
    print("SEASON IN AVAILABLE:", season)
    queryset = (
        EvaluationInvitation.objects
        .filter(
            season=season,
            status="ACCEPTED",
            user__volunteer_profile__status=VolunteerProfile.APPROVED
        )
        .select_related(
            "user",
            "user__volunteer_profile"
        )
    )

    if specialization:
        queryset = queryset.filter(
            user__volunteer_profile__specialization__icontains=specialization
        )

    if skills:
        queryset = queryset.filter(
            Q(user__volunteer_profile__primary_skills__icontains=skills)
            |
            Q(user__volunteer_profile__additional_skills__contains=[skills])
        )

    return queryset