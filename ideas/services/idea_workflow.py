from core.exceptions import BusinessLogicException
from ideas.models import IdeaStatus


class IdeaWorkflow:

    TRANSITIONS = {

        IdeaStatus.DRAFT: [
            IdeaStatus.SUBMITTED
        ],

        IdeaStatus.SUBMITTED: [
            IdeaStatus.PRE_ACCEPTED,
            IdeaStatus.REJECTED,
        ],

        IdeaStatus.PRE_ACCEPTED: [
            IdeaStatus.BOOTCAMP
        ],

        IdeaStatus.BOOTCAMP: [
            IdeaStatus.EVALUATION,
            IdeaStatus.BOOTCAMP_FAILED,
        ],

        IdeaStatus.EVALUATION: [
            IdeaStatus.EVALUATED
        ],

        IdeaStatus.EVALUATED: [
            IdeaStatus.ACCEPTED,
            IdeaStatus.REJECTED,
        ],

        IdeaStatus.ACCEPTED: [
            IdeaStatus.INCUBATION
        ],

        IdeaStatus.INCUBATION: [
            IdeaStatus.EXHIBITION,
            IdeaStatus.GRADUATED_NEGATIVE,
        ],

        IdeaStatus.EXHIBITION: [
            IdeaStatus.GRADUATED_POSITIVE,
            IdeaStatus.GRADUATED_NEGATIVE,
        ],
    }

    @classmethod
    def can_transition(cls, from_status, to_status):
        return to_status in cls.TRANSITIONS.get(from_status, [])

    @classmethod
    def transition(cls, idea, to_status, user=None):

        if not cls.can_transition(idea.status, to_status):
            raise BusinessLogicException(
                f"Cannot move from {idea.status} to {to_status}"
            )

        old_status = idea.status
        idea.status = to_status
        idea.save()

        from core.events import EventBus

        EventBus.emit(
            "idea_status_changed",
            idea=idea,
            old_status=old_status,
            new_status=to_status,
            user=user
        )