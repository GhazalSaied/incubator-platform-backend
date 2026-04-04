from rest_framework.exceptions import ValidationError
from ideas.phases import get_current_phase
from bootcamp.models import BootcampSession


def create_session(serializer):
    season = serializer.validated_data.get("season")

    phase = get_current_phase(season)

    if not phase or phase.phase != "bootcamp":
        raise ValidationError("ليس وقت المعسكر")

    return serializer.save()