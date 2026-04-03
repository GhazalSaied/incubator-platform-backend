from core.roles import user_has_role, user_has_any_role
from core.exceptions import BusinessLogicException


class IdeaPermissions:

    @staticmethod
    def can_submit(user, idea):
        if idea.owner != user:
            raise BusinessLogicException("Not your idea")

    @staticmethod
    def can_accept(user):
        if not user_has_any_role(user, ["ADMIN", "EVALUATOR"]):
            raise BusinessLogicException("Not allowed to accept ideas")

    @staticmethod
    def can_move_to_bootcamp(user):
        if not user_has_role(user, "ADMIN"):
            raise BusinessLogicException("Only admin can move to bootcamp")