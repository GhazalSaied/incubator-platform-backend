from rest_framework.exceptions import ValidationError
from ideas.phases import get_current_phase

def create_bootcamp_session(serializer, season):

    # ✅ نجيب المرحلة الحالية
    phase = get_current_phase(season)

    if not phase:
        raise ValidationError("لا يوجد مرحلة حالية")

    if phase.phase != "bootcamp":
        raise ValidationError("ليس وقت المعسكر")

    return serializer.save(phase=phase)