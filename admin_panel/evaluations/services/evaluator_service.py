
from evaluations.models import EvaluationCriterion

from .settings_service import SettingsService

@staticmethod
def get_criteria_for_evaluator():

    settings = SettingsService.get()

    if not settings.is_published:
        return []

    return EvaluationCriterion.objects.filter(is_active=True)