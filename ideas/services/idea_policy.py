from core.roles import user_has_any_role , user_has_role
from core.exceptions import BusinessLogicException
from ideas.models import IdeaStatus


class IdeaPolicy:

    @staticmethod
    def can_accept(user, idea):

        if idea.status != IdeaStatus.EVALUATION:
            raise BusinessLogicException("Idea not in evaluation stage")

        if not user_has_any_role(user, ["ADMIN", "EVALUATOR"]):
            raise BusinessLogicException("Not allowed")


    @staticmethod
    def can_submit(user, idea):

        if idea.owner != user:
            raise BusinessLogicException("Not your idea")

        if idea.status != IdeaStatus.DRAFT:
            raise BusinessLogicException("Already submitted")
        
    

    @staticmethod
    def can_start_evaluation(user, idea):

        if not user_has_role(user, "ADMIN"):
            raise BusinessLogicException("Only admin can start evaluation")

        if idea.status != IdeaStatus.SUBMITTED:
            raise BusinessLogicException("Invalid state")
     
        
    
    @staticmethod
    def can_move_from_bootcamp(user, idea):

        if not user_has_role(user, "ADMIN"):
            raise BusinessLogicException("Only admin allowed")

        if idea.attendance_rate < 75:
            raise BusinessLogicException("Attendance below 75%")
            
    
