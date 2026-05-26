from django.db.models import Avg, Sum
from accounts.constants import SystemRoles
from accounts.role_service import RoleService
from core.events import EventBus
from evaluations.models import Evaluation
import ideas
from ideas.models import Idea,IdeaStatus
from django.core.exceptions import ValidationError
from ideas.services.state.idea_state_service import IdeaStateService
from notifications.services.notification_service import NotificationService
from evaluations.models import EvaluationAssignment
from django.db import transaction

from django.db.models import Prefetch
from evaluations.models import Evaluation, EvaluationAssignment, EvaluationScore
from ideas.models import Idea
from evaluations.models import EvaluationAssignment, Evaluation


from evaluations.models import (
    Evaluation,
    EvaluationAssignment,
)


class EvaluationStatusService:

    @staticmethod
    def is_fully_evaluated(idea):

        assignments = EvaluationAssignment.objects.filter(
            idea=idea
        )
        

        if not assignments.exists():
            return False

        evaluator_ids = list(
            assignments.values_list(
                "evaluator_id",
                flat=True
            ).distinct()
        )

        submitted_count = Evaluation.objects.filter(
            idea=idea,
            evaluator_id__in=evaluator_ids,
            is_submitted=True
        ).values(
            "evaluator_id"
        ).distinct().count()

        return submitted_count == len(evaluator_ids)

from django.db.models import Prefetch

from evaluations.models import Evaluation
from ideas.models import Idea


class EvaluationResultsService:

    @staticmethod
    def get_results(*, sector=None, status=None):

        ideas = Idea.objects.select_related(
            "owner"
        )

        if sector:
            ideas = ideas.filter(
                sector=sector
            )

        evaluations_qs = Evaluation.objects.filter(
            is_submitted=True
        ).prefetch_related("scores")

        ideas = ideas.prefetch_related(
            Prefetch(
                "evaluations",
                queryset=evaluations_qs
            )
        )

        data = []

        for idea in ideas:

            evaluations = idea.evaluations.all()

            is_fully_evaluated = (
                EvaluationStatusService.is_fully_evaluated(idea)
            )

            evaluation_status = (
                "تم التقييم"
                if is_fully_evaluated
                else "قيد التقييم"
            )

            total_scores = [
                sum(score.score for score in ev.scores.all())
                for ev in evaluations
            ]

            average_score = (
                sum(total_scores) / len(total_scores)
                if total_scores else 0
            )

            if status and status != evaluation_status:
                continue

            data.append({
                "idea_id": idea.id,

                "project_name": idea.title,

                "owner_email": idea.owner.email,

                "sector": idea.sector,

                "target_audience": idea.target_audience,

                "evaluation_status": evaluation_status,

                "evaluation_result": (
                    round(average_score, 2)
                    if is_fully_evaluated
                    else None
                )
            })

        return data
class EvaluationDetailsService:

    @staticmethod
    def get_idea_evaluation_details(*, idea):

        evaluations = Evaluation.objects.filter(
            idea=idea,
            is_submitted=True
        ).select_related(
            "evaluator",
            "evaluator__volunteer_profile"
        )

        assignments_map = {
            a.evaluator_id: a.meeting_date
            for a in EvaluationAssignment.objects.filter(idea=idea)
        }

        results = []

        for evaluation in evaluations:

            evaluator = evaluation.evaluator
            profile = getattr(evaluator, "volunteer_profile", None)
            meeting_date = assignments_map.get(evaluator.id)
            results.append({
                "evaluator_name": evaluator.full_name,

                "evaluator_image": getattr(evaluator, "user.avatar", None),

                "specialization": profile.specialization if profile else None,


                "meeting_date": (
                meeting_date.strftime("%d/%m/%Y")
                if meeting_date else None
                ),

                "notes": evaluation.notes,
            })

        return results
    
    
    
    


class EvaluationDecisionService:

    @transaction.atomic
    @staticmethod
    def _validate_decision(idea):

        
        if not idea.status == IdeaStatus.EVALUATED:
            raise ValidationError("لا يمكن اتخاذ قرار قبل اكتمال جميع التقييمات")

        #  منع التكرار
        if idea.status in [IdeaStatus.ACCEPTED, IdeaStatus.REJECTED]:
            raise ValidationError("تم اتخاذ قرار مسبقاً لهذه الفكرة")

    # ----------------------------------------
    @transaction.atomic
    @staticmethod
    def accept_idea(*, idea):

        EvaluationDecisionService._validate_decision(idea)
        new_status = IdeaStatus.ACCEPTED
        IdeaStateService.change_status(
        idea=idea,
        to_status=new_status,
        source="evaluation_decision"
    )
        EventBus.emit(
            "idea_accepted",idea=idea,actor=None )


        return idea

    # ----------------------------------------
    @transaction.atomic
    @staticmethod
    def reject_idea(*, idea):

        EvaluationDecisionService._validate_decision(idea)

        new_status = IdeaStatus.REJECTED
        IdeaStateService.change_status(
        idea=idea,
        to_status=new_status,
        source="evaluation_decision"
    )
        
        RoleService.remove_role(
            user=idea.owner,
            role_code=SystemRoles.IDEA_OWNER
        )
        EventBus.emit(
            "idea_rejected",idea=idea,actor=None )
        return idea
    
    
    





