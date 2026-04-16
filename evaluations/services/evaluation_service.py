from django.utils import timezone
from django.core.exceptions import ValidationError
from core.events import EventBus

from evaluations.models import (
    Evaluation,
    EvaluationScore,
    EvaluationAssignment,
    EvaluationCriterion,
)


class EvaluationService:

    # ////////////////////////////////// CREATE OR UPDATE //////////////////////////////////

    @staticmethod
    def create_or_update_evaluation(user, idea, data):
        assignment = EvaluationAssignment.objects.filter(
            evaluator=user,
            idea=idea
        ).first()

        if not assignment:
            raise ValidationError("غير مصرح لك بتقييم هذه الفكرة")

        evaluation, _ = Evaluation.objects.get_or_create(
            evaluator=user,
            idea=idea,
            season=assignment.season
        )

        if evaluation.is_submitted:
            raise ValidationError("لا يمكن تعديل تقييم تم إرساله")

        evaluation.notes = data.get("notes", evaluation.notes)
        evaluation.save()

        scores_data = data.get("scores", [])
        criterion = EvaluationCriterion.objects.get(id=score_data["criterion"])
        for score_data in scores_data:
            criterion = EvaluationCriterion.objects.get(id=score_data["criterion"])
            if score_data["score"] > criterion.max_score:
                raise ValidationError("Score exceeds max value")
            EvaluationScore.objects.update_or_create(
                evaluation=evaluation,
                criterion_id=score_data["criterion"],
                defaults={"score": score_data["score"]}
            )

        return evaluation

    # ////////////////////////////////// SUBMIT //////////////////////////////////

    @staticmethod
    def submit_evaluation(user, idea):
        try:
            evaluation = Evaluation.objects.get(
                evaluator=user,
                idea=idea
            )
        except Evaluation.DoesNotExist:
            raise ValidationError("لا يوجد تقييم لهذه الفكرة")

        if evaluation.is_submitted:
            raise ValidationError("تم إرسال التقييم مسبقاً")
        
        if evaluation.scores.count() == 0:
            raise ValidationError("لا يمكن إرسال تقييم فارغ")

        total_criteria = EvaluationCriterion.objects.filter(is_active=True).count()
        if evaluation.scores.count() < total_criteria:
            raise ValidationError("يجب تقييم جميع المعايير")

        evaluation.is_submitted = True
        evaluation.submitted_at = timezone.now()
        evaluation.save()

        EventBus.emit("evaluation_submitted", {
            "evaluation": evaluation,
            "idea": idea,
            "user": user,
            "action_url": f"/ideas/{idea.id}/evaluation"
        })

        EvaluationAssignment.objects.filter(
            evaluator=user,
            idea=idea
        ).update(is_completed=True)

        return evaluation

    # ////////////////////////////////// ASSIGNMENTS //////////////////////////////////

    @staticmethod
    def get_user_assignments(user):
        return EvaluationAssignment.objects.filter(
            evaluator=user
        ).select_related("idea")

    @staticmethod
    def get_user_assignments_data(user):
        assignments = EvaluationAssignment.objects.filter(
            evaluator=user
        ).select_related("idea")

        return [
            {
                "id": a.id,
                "idea_id": a.idea.id,
                "title": a.idea.title,
                "meeting_date": a.meeting_date,
                "is_completed": a.is_completed
            }
            for a in assignments
        ]

    # ////////////////////////////////// ASSIGNMENT DETAIL //////////////////////////////////

    @staticmethod
    def get_assignment_detail(user, assignment_id):
        return EvaluationAssignment.objects.select_related("idea").get(
            id=assignment_id,
            evaluator=user
        )

    # ////////////////////////////////// DASHBOARD //////////////////////////////////

@staticmethod
def get_dashboard(user):
    assignments = EvaluationAssignment.objects.filter(
        evaluator=user
    ).select_related("idea")

    total = assignments.count()
    completed = assignments.filter(is_completed=True).count()

    #  أقرب جلسة
    next_assignment = assignments.filter(
        meeting_date__gte=timezone.now()
    ).order_by("meeting_date").first()

    data = []

    for a in assignments:
        evaluation = Evaluation.objects.filter(
            evaluator=user,
            idea=a.idea
        ).only("is_submitted").first()

        data.append({
            "assignment_id": a.id,
            "idea_id": a.idea.id,
            "title": a.idea.title,
            "meeting_date": a.meeting_date,
            "is_completed": a.is_completed,
            "is_submitted": evaluation.is_submitted if evaluation else False
        })

    return {
        "stats": {
            "total": total,
            "completed": completed,
            "remaining": total - completed
        },

        "next_meeting": {
            "idea_title": next_assignment.idea.title,
            "meeting_date": next_assignment.meeting_date
        } if next_assignment else None,

        "assignments": data
    }

    # ////////////////////////////////// MY EVALUATION DETAIL //////////////////////////////////

@staticmethod
def get_user_evaluation_detail(user, idea_id):
    evaluation = Evaluation.objects.filter(
        evaluator=user,
        idea_id=idea_id
    ).prefetch_related("scores__criterion").first()

    if not evaluation:
        return None

    scores = [
        {
            "criterion": s.criterion.title,
            "score": s.score,
            "max_score": s.criterion.max_score
        }
        for s in evaluation.scores.all()
    ]

    return {
        "idea_id": evaluation.idea.id,
        "notes": evaluation.notes,
        "is_submitted": evaluation.is_submitted,
        "scores": scores
    }