from rest_framework.exceptions import ValidationError
from ideas.phases import get_current_phase
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase
from core.events import EventBus
from django.db import transaction

@transaction.atomic
def create_bootcamp_session(serializer, season):
    phase = SeasonPhaseService.get_current_phase(season)

    if not phase:
        raise ValidationError("لا يوجد مرحلة حالية")
    session = serializer.save(phase=phase)

    # 🔥 Trigger Event
    EventBus.emit(
        "bootcamp_session_created",
        session=session
    )

    return session

class BootcampSessionQueryService:

    @staticmethod
    def get_trainer_name(session):
        if not session.trainer:
            return None

        return getattr(session.trainer, "full_name", None) or getattr(session.trainer, "username", None)

    # ----------------------------------

    @staticmethod
    def get_time_range(session):
        if not session.start_time or not session.end_time:
            return None

        return f"{session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}"