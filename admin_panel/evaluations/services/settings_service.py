from evaluations.models import EvaluationSettings


class SettingsService:

    @staticmethod
    def get():
        settings = EvaluationSettings.objects.first()

        if not settings:
            settings = EvaluationSettings.objects.create()

        return settings