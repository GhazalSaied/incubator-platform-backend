from django.utils import timezone

from bootcamp.serializers import (
    BootcampSessionsTableSerializer,
    NextBootcampSessionSerializer,
)

from bootcamp.services.bootcamp_owner_service import (
    BootcampOwnerService,
)

from evaluations.serializers import (
    EvaluationSessionStatusSerializer,
    IncubationOverviewSerializer,
)

from evaluations.services.evaluation_service import (
    EvaluationService,
)

from ideas.models import (
    IdeaStatus,
    TeamMember,
)

from ideas.serializers import (
    ExhibitionFormDetailsSerializer,
)

from ideas.services.exhibition_service import (
    ExhibitionService,
)

from ideas.services.idea_service import IdeaService
from rest_framework.exceptions import ValidationError

class EvaluationStatuses:
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    COMPLETED = "COMPLETED"


class BaseDashboardProvider:

    @classmethod
    def get_data(cls, *, user, idea):
        raise NotImplementedError


# /////////////////////////////////////////////////////////////////
# BOOTCAMP
# /////////////////////////////////////////////////////////////////

class BootcampDashboardProvider(
    BaseDashboardProvider
):

    @classmethod
    def get_data(cls, *, user, idea):

        next_session = (
            BootcampOwnerService
            .get_next_session(idea=idea)
        )

        sessions = (
            BootcampOwnerService
            .get_all_bootcamp_sessions(
                idea=idea
            )
        )

        return {
            "next_session": (
                NextBootcampSessionSerializer(
                    next_session
                ).data
                if next_session
                else None
            ),

            "sessions": (
                BootcampSessionsTableSerializer(
                    sessions,
                    many=True
                ).data
            ),

            "absence_request_enabled": (
                next_session is not None
            ),
        }


# /////////////////////////////////////////////////////////////////
# EVALUATION
# /////////////////////////////////////////////////////////////////

class EvaluationDashboardProvider(
    BaseDashboardProvider
):

    @classmethod
    def get_data(cls, *, user, idea):

        data = (
            EvaluationService
            .get_idea_evaluation_session_status(
                user=user,
                idea=idea,
            )
        )

        serialized = (
            EvaluationSessionStatusSerializer(
                data
            ).data
        )

        return {
            **serialized,
            "consultation_request_available": True,
        }


# /////////////////////////////////////////////////////////////////
# INCUBATION
# /////////////////////////////////////////////////////////////////

class IncubationDashboardProvider(
    BaseDashboardProvider
):

    @classmethod
    def get_data(cls, *, user, idea):

        data = (
            EvaluationService
            .get_incubation_overview_for_incubatee(
                user=user,
                idea=idea,
            )
        )

        serialized = (
            IncubationOverviewSerializer(
                data
            ).data
        )

        return {
            **serialized,
            "can_request_consultation": True,
            "can_request_team": True,
        }


# /////////////////////////////////////////////////////////////////
# EXHIBITION
# /////////////////////////////////////////////////////////////////

class ExhibitionDashboardProvider(
    BaseDashboardProvider
):

    @classmethod
    def get_data(cls, *, user, idea):

        is_owner = (
            idea.owner_id == user.id
        )

        dashboard = (
            ExhibitionService
            .get_exhibition_dashboard(user)
        )

        form_data = None

        if is_owner:
            form_data = (
                ExhibitionFormDetailsSerializer(
                    dashboard["form"]
                ).data
            )

        submission_data = (
            dashboard["submission"].data
            if dashboard["submission"]
            else None
        )

        return {
            "exhibition_date": (
                idea.season.exhibition_datetime
            ),

            "is_owner": is_owner,

            "can_edit": (
                is_owner
                and dashboard["submission"] is None
            ),

            "form": form_data,

            "submitted_data": submission_data,
        }


# /////////////////////////////////////////////////////////////////
# GRADUATED NEGATIVE
# /////////////////////////////////////////////////////////////////

class GraduatedNegativeDashboardProvider(
    BaseDashboardProvider
):

    @classmethod
    def get_data(cls, *, user, idea):

        return {
            "message": (
                "غير مؤهل للوصول إلى مرحلة المعرض"
            )
        }


# /////////////////////////////////////////////////////////////////
# PROVIDERS REGISTRY
# /////////////////////////////////////////////////////////////////

STAGE_PROVIDERS = {

    IdeaStatus.BOOTCAMP:
        BootcampDashboardProvider,

    IdeaStatus.EVALUATION :
        EvaluationDashboardProvider,

    IdeaStatus.EVALUATED:
        EvaluationDashboardProvider,

    IdeaStatus.INCUBATION:
        IncubationDashboardProvider,

    IdeaStatus.GRADUATED_POSITIVE:
        ExhibitionDashboardProvider,

    IdeaStatus.GRADUATED_NEGATIVE:
        GraduatedNegativeDashboardProvider,
}


# /////////////////////////////////////////////////////////////////
# MAIN DASHBOARD SERVICE
# /////////////////////////////////////////////////////////////////

class IdeaDashboardService:

    @staticmethod
    def get_user_dashboard(user):

        try:
            idea = (
                IdeaService.get_dashboard_idea(user)
            )

        except ValidationError :
            return {
                "current_stage": None,
                "data": None,
            }

        provider = STAGE_PROVIDERS.get(
            idea.status
        )

        if not provider:

            return {
                "current_stage": idea.status,
                "data": None,
            }

        data = provider.get_data(
            user=user,
            idea=idea,
        )

        return {
            "current_stage": idea.status,
            "data": data,
        }