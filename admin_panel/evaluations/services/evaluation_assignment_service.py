from django.core.exceptions import ValidationError
from django.db import transaction

from evaluations.models import EvaluationAssignment, EvaluationInvitation


class EvaluationAssignmentService:

    @staticmethod
    @transaction.atomic
    def assign_evaluators_to_idea(
        *,
        idea,
        evaluators_ids,
        season
    ):
        """
        Assign evaluators to an idea based on accepted invitations
        """

        if not evaluators_ids:
            raise ValidationError("يجب اختيار مقيم واحد على الأقل")

        # 🟢 جلب الدعوات المقبولة فقط
        accepted_invitations = EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED",
            user_id__in=evaluators_ids
        ).select_related("user")

        if not accepted_invitations.exists():
            raise ValidationError("لا يوجد مقيمون مقبولون بهذه المعطيات")

        assignments = []
        skipped_users = []

        for invitation in accepted_invitations:

            evaluator = invitation.user

            # 🛑 1. منع صاحب الفكرة
            if evaluator.id == idea.owner_id:
                skipped_users.append({
                    "user_id": evaluator.id,
                    "reason": "OWNER_CANNOT_EVALUATE"
                })
                continue

            # 🛑 2. منع التكرار
            exists = EvaluationAssignment.objects.filter(
                idea=idea,
                evaluator=evaluator,
                season=season
            ).exists()

            if exists:
                skipped_users.append({
                    "user_id": evaluator.id,
                    "reason": "ALREADY_ASSIGNED"
                })
                continue

            # 🟢 إنشاء التعيين
            assignment = EvaluationAssignment.objects.create(
                evaluator=evaluator,
                idea=idea,
                season=season,
                invitation=invitation
            )

            assignments.append(assignment)

        return {
            "assigned": assignments,
            "skipped": skipped_users
        }