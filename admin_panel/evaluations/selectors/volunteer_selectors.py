from evaluations.models import EvaluationInvitation
from volunteers.models import VolunteerProfile
from django.db.models import Q

def get_available_season_evaluators(
    season,
    volunteer_type=None,
    skills=None,
):
    """
    Returns accepted evaluators for current season
    with optional filtering by specialization and skills
    """

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

    if volunteer_type:
        queryset = queryset.filter(
            user__volunteer_profile__volunteer_type__icontains=volunteer_type
        )

    if skills:
        queryset = queryset.filter(
            Q(user__volunteer_profile__primary_skills__icontains=skills)
            |
            Q(user__volunteer_profile__additional_skills__icontains=skills)
        )

    return queryset