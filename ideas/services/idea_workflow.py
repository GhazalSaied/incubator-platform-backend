from core.exceptions import BusinessLogicException
from ideas.models import IdeaStatus


#////////////// بتمنع ال transition الغلط /////////////////

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
    def validate_transition(cls, from_status, to_status):
        if not cls.can_transition(from_status, to_status):
            raise BusinessLogicException(
                f"Cannot move from {from_status} to {to_status}"
            )