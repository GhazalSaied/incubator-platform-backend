from django.apps import AppConfig
from core.events import EventBus


class EvaluationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evaluations'

    def ready(self):

        from evaluations.handlers.evaluation_workflow_handlers import (
            handle_evaluation_completed
        )

        # workflow automation
        EventBus.register(
            "evaluation_submitted",
            handle_evaluation_completed
        )