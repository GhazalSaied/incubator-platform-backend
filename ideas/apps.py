from django.apps import AppConfig
from core.events import EventBus



class IdeasConfig(AppConfig):
    name = 'ideas'
    def ready(self):
        from ideas.events.idea_phase_transition_handler import (handle_preaccepted_to_bootcamp)
        EventBus.register("idea_status_changed",handle_preaccepted_to_bootcamp)
        from ideas.services.phase_trigger_service import PhaseTriggerService
        