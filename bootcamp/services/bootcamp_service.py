from bootcamp.models import (
    BootcampSession,
    BootcampAttendance,
)
from ideas.models import (
    Idea,
    IdeaStatus,
)


class VolunteerBootcampService:
    @staticmethod
    def get_my_sessions(user):
        return (
            BootcampSession.objects
            .filter(
                trainer=user,
                is_active=True,
                phase__phase="BOOTCAMP",
            )
            .order_by("date", "start_time")
        )

    @staticmethod
    def get_session_or_none(session_id):
        try:
            return BootcampSession.objects.get(
                id=session_id,
                is_active=True,
            )
        except BootcampSession.DoesNotExist:
            return None

    @staticmethod
    def get_pending_bootcamp_ideas_for_session(session):
        attended_ideas_ids = BootcampAttendance.objects.filter(
            session=session
        ).values_list(
            "idea_id",
            flat=True
        )

        return (
            Idea.objects
            .select_related("owner")
            .filter(
                status=IdeaStatus.BOOTCAMP
            )
            .exclude(
                id__in=attended_ideas_ids
            )
            .order_by("-created_at")
        )

    @staticmethod
    def create_attendance(
        *,
        session,
        idea,
        status,
        marked_by,
    ):
        return BootcampAttendance.objects.create(
            session=session,
            idea=idea,
            status=status,
            is_submitted=True,
            marked_by=marked_by,
        )