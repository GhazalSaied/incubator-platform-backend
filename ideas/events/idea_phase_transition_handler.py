from ideas.models import IdeaStatus, Idea
from ideas.services.state.idea_state_service import IdeaStateService
from core.events import EventBus
from django.db import transaction
from ideas.phases import SeasonPhase

from ideas.services.state.idea_state_service import (
    IdeaStateService
)
def handle_preaccepted_to_bootcamp(payload):
    idea = payload["idea"]

    if payload["new_status"] != IdeaStatus.PRE_ACCEPTED:
        return

    IdeaStateService.change_status(
        idea=idea,
        to_status=IdeaStatus.BOOTCAMP,
        source="auto_phase_transition"
    )
    
    
    
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

