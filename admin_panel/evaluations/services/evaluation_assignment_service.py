from rest_framework.exceptions import ValidationError
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
        Assign evaluators to an idea based on accepted invitations.
        """

        if not evaluators_ids:
            raise ValidationError(
                "يجب اختيار مقيم واحد على الأقل"
            )

        # إزالة التكرار من الـ IDs
        evaluators_ids = list(set(evaluators_ids))

        accepted_invitations = EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED",
            user_id__in=evaluators_ids
        ).select_related("user")

        accepted_user_ids = set(
            accepted_invitations.values_list("user_id", flat=True)
        )

        skipped_users = []

        # المقيمون الذين تم اختيارهم ولكن ليس لديهم دعوة مقبولة
        invalid_user_ids = set(evaluators_ids) - accepted_user_ids

        for user_id in invalid_user_ids:
            skipped_users.append({
                "user_id": user_id,
                "reason": "هذا المستخدم لا يملك دعوة تقييم مقبولة في الموسم الحالي"
            })

        assignments = []

        for invitation in accepted_invitations:

            evaluator = invitation.user

            # 1. منع صاحب الفكرة من تقييم مشروعه
            if evaluator.id == idea.owner_id:
                skipped_users.append({
                    "user_id": evaluator.id,
                    "reason": "لا يمكن لصاحب الفكرة تقييم مشروعه"
                })
                continue

            # 2. منع التكرار
            exists = EvaluationAssignment.objects.filter(
                idea=idea,
                evaluator=evaluator,
                season=season
            ).exists()

            if exists:
                skipped_users.append({
                    "user_id": evaluator.id,
                    "reason": "تم تعيين هذا المقيم مسبقاً لهذا المشروع"
                })
                continue

            # 3. إنشاء التعيين
            assignment = EvaluationAssignment.objects.create(
                evaluator=evaluator,
                idea=idea,
                season=season,
                invitation=invitation
            )

            assignments.append(assignment)

        # إذا لم يتم تعيين أي مقيم
        if not assignments:
            if skipped_users:
                raise ValidationError(
                    "لم يتم تعيين أي مقيم. يرجى التحقق من المقيمين المختارين."
                )

            raise ValidationError(
                "لم يتم تعيين أي مقيم"
            )

        return {
            "assigned": assignments,
            "skipped": skipped_users
        }