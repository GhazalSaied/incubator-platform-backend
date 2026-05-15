from datetime import datetime

from bootcamp.models import (
    BootcampSession,
    BootcampAbsenceRequest,
)
from ideas.models import IdeaStatus
from ideas.services.idea_service import IdeaService
from core.events import EventBus


class BootcampOwnerService:
    @staticmethod
    def get_user_bootcamp_idea(user):
        idea = IdeaService.get_user_idea(user)

        if idea.status != IdeaStatus.BOOTCAMP:
            raise ValueError(
                "Your idea is not in BOOTCAMP stage."
            )

        return idea

    @staticmethod
    def get_all_bootcamp_sessions():
        return (
            BootcampSession.objects
            .select_related("trainer")
            .filter(
                phase__phase="BOOTCAMP",
                is_active=True,
            )
            .order_by("date", "start_time")
        )

    @staticmethod
    def get_next_session():
        now = datetime.now()

        sessions = (
            BootcampSession.objects
            .filter(
                phase__phase="BOOTCAMP",
                is_active=True,
                date__isnull=False,
                start_time__isnull=False,
            )
            .order_by("date", "start_time")
        )

        for session in sessions:
            session_datetime = datetime.combine(
                session.date,
                session.start_time
            )

            if session_datetime >= now:
                return session

        return None

    @staticmethod
    def create_absence_request(
        *,
        user,
        reason,
    ):
        idea = BootcampOwnerService.get_user_bootcamp_idea(
            user=user
        )

        session = BootcampOwnerService.get_next_session()

        if not session:
            raise ValueError(
                "لا يوجد جلسة قادمة حالياً."
            )

        existing = (
            BootcampAbsenceRequest.objects.filter(
                idea=idea,
                session=session
            )
            .exists()
        )

        if existing:
            raise ValueError(
                "تم إرسال طلب غياب مسبق لهذه الجلسة."
            )

        absence_request = (
            BootcampAbsenceRequest.objects.create(
                idea=idea,
                session=session,
                reason=reason,
            )
        )

        EventBus.emit(
            "bootcamp_absence_request_submitted",
            absence_request=absence_request,
            actor=user,
        )

        return absence_request