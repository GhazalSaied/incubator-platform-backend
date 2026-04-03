from ideas.models import IdeaStatus
from core.exceptions import BusinessLogicException


class IdeaRules:

    @staticmethod
    def can_submit(idea):
        if idea.status != IdeaStatus.DRAFT:
            raise BusinessLogicException("Only draft ideas can be submitted")

    @staticmethod
    def can_move_to_bootcamp(idea):
        if idea.status != IdeaStatus.UNDER_REVIEW:
            raise BusinessLogicException("Idea must be under review")

    @staticmethod
    def can_accept(idea):
        if idea.status != IdeaStatus.EVALUATION:
            raise BusinessLogicException("Idea must be in evaluation phase")