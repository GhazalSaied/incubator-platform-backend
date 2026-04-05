from django.utils import timezone
from django.core.exceptions import ValidationError

from evaluations.models import (
    Evaluation,
    EvaluationScore,
    EvaluationAssignment,
)


class EvaluationService:

    # ////////////////////////////////// CREATE OR UPDATE //////////////////////////////////

    @staticmethod
    def create_or_update_evaluation(user, idea, data):
        assignment = EvaluationAssignment.objects.filter(
            evaluator=user,
            idea=idea
        ).exists()

        if not assignment:
            raise ValidationError("غير مصرح لك بتقييم هذه الفكرة")

        evaluation, _ = Evaluation.objects.get_or_create(
            evaluator=user,
            idea=idea,
            defaults={"season": assignment.season}
        )

        if evaluation.is_submitted:
            raise ValidationError("لا يمكن تعديل تقييم تم إرساله")

        evaluation.notes = data.get("notes", evaluation.notes)
        evaluation.save()

        scores_data = data.get("scores", [])

        for score_data in scores_data:
            if score_data["score"] > score_data["criterion"].max_score:
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

        evaluation.is_submitted = True
        evaluation.submitted_at = timezone.now()
        evaluation.save()

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

        data = []

        for a in assignments:
            evaluation = Evaluation.objects.filter(
                evaluator=user,
                idea=a.idea
            ).exists()

            data.append({
                "assignment_id": a.id,
                "idea_id": a.idea.id,
                "title": a.idea.title,
                "meeting_date": a.meeting_date,
                "is_completed": a.is_completed,
                "is_submitted": evaluation.is_submitted if evaluation else False
            })

        return data

    # ////////////////////////////////// MY EVALUATION DETAIL //////////////////////////////////

    @staticmethod
    def get_user_evaluation_detail(user, idea_id):
        evaluation = Evaluation.objects.filter(
            evaluator=user,
            idea_id=idea_id
        ).prefetch_related("scores__criterion").exists()

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