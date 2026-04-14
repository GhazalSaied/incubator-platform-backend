from django.db.models import Avg, Sum
from evaluations.models import Evaluation
import ideas
from ideas.models import Idea,IdeaStatus
from django.core.exceptions import ValidationError
from notifications.services.notification_service import NotificationService
from evaluations.models import EvaluationAssignment
from .phase_transition_service import PhaseTransitionService

from django.db.models import Prefetch
from evaluations.models import Evaluation, EvaluationAssignment, EvaluationScore
from ideas.models import Idea
from evaluations.models import EvaluationAssignment, Evaluation


class EvaluationStatusService:

    @staticmethod
    def is_fully_evaluated(idea):

        assignments = EvaluationAssignment.objects.filter(
            idea=idea
        )

        if not assignments.exists():
            return False

        evaluators_ids = assignments.values_list(
            "evaluator_id", flat=True
        )

        submitted_count = Evaluation.objects.filter(
            idea=idea,
            evaluator_id__in=evaluators_ids,
            is_submitted=True
        ).values("evaluator_id").distinct().count()

        return submitted_count == len(evaluators_ids)


class EvaluationResultsService:

    @staticmethod
    def get_results(*, sector=None, status=None):

        ideas = Idea.objects.select_related("owner")

        if sector:
            ideas = ideas.filter(sector=sector)

        # 🟢 preload كل التقييمات
        evaluations_qs = Evaluation.objects.filter(
            is_submitted=True
        ).prefetch_related("scores")

        ideas = ideas.prefetch_related(
            Prefetch("evaluations", queryset=evaluations_qs)
        )

        data = []

        for idea in ideas:

            evaluations = idea.evaluations.all()

            # 🔥 الحالة الصح
            is_fully_evaluated = EvaluationStatusService.is_fully_evaluated(idea)

            evaluation_status = (
                "تم التقييم" if is_fully_evaluated else "قيد التقييم"
            )

            # 🟢 حساب السكور
            total_scores = [
                sum(score.score for score in ev.scores.all())
                for ev in evaluations
            ]

            average_score = (
                sum(total_scores) / len(total_scores)
                if total_scores else 0
            )

            # 🟢 فلترة
            if status and status != evaluation_status:
                continue

            data.append({
                "idea_id": idea.id,
                "title": idea.title,
                "owner_email": idea.owner.email,
                "sector": idea.sector,
                "evaluation_status": evaluation_status,
                "average_score": round(average_score, 2)
            })

        return data
class EvaluationDetailsService:

    @staticmethod
    def get_idea_evaluation_details(*, idea):

        # 🟢 جلب التقييمات مع المقيم + البروفايل
        evaluations = Evaluation.objects.filter(
            idea=idea,
            is_submitted=True
        ).select_related(
            "evaluator",
            "evaluator__volunteer_profile"
        )

        # 🟢 mapping سريع للـ meeting_date
        assignments_map = {
            a.evaluator_id: a.meeting_date
            for a in EvaluationAssignment.objects.filter(idea=idea)
        }

        results = []

        for evaluation in evaluations:

            evaluator = evaluation.evaluator
            profile = getattr(evaluator, "volunteer_profile", None)

            results.append({
                "evaluator_name": evaluator.full_name,

                # 🟢 صورة (إذا عندك image بالحساب)
                "evaluator_image": getattr(evaluator, "user.avatar", None),

                # 🟢 اختصاص (من البروفايل)
                "specialization": profile.primary_skills if profile else None,

                # 🟢 تاريخ الجلسة
                "meeting_date": assignments_map.get(evaluator.id),

                # 🟢 الملاحظات
                "notes": evaluation.notes,
            })

        return results
    
    
    
    


class EvaluationDecisionService:

    @staticmethod
    def _try_finish_evaluation_phase(season):

        remaining = season.ideas.filter(
            status=IdeaStatus.EVALUATION
        ).count()

        print("Remaining ideas:", remaining)  # debug مؤقت

        if remaining == 0:

            PhaseTransitionService._move_to_incubation(season)

    @staticmethod
    def _validate_decision(idea, message):

        # 🟢 تحقق من المرحلة
        if idea.status != IdeaStatus.EVALUATION:
            raise ValidationError("لا يمكن اتخاذ قرار خارج مرحلة التقييم")
        # 🟢 لازم التقييم يكون مكتمل
        if not EvaluationStatusService.is_fully_evaluated(idea):
            raise ValidationError("لا يمكن اتخاذ قرار قبل اكتمال جميع التقييمات")

        
        

        # 🟢 منع التكرار
        if idea.status in [IdeaStatus.ACCEPTED, IdeaStatus.REJECTED]:
            raise ValidationError("تم اتخاذ قرار مسبقاً لهذه الفكرة")

        # 🟢 الرسالة إجبارية
        if not message or not message.strip():
            raise ValidationError("الرسالة مطلوبة")

    # ----------------------------------------

    @staticmethod
    def accept_idea(*, idea, message):

        EvaluationDecisionService._validate_decision(idea, message)

        idea.status = IdeaStatus.ACCEPTED
        idea.save(update_fields=["status"])
        EvaluationDecisionService._try_finish_evaluation_phase(idea.season)
        NotificationService.send(
            user=idea.owner,
            title="تم قبول فكرتك 🎉",
            message=message,
            action_type="VIEW_IDEA",
            action_url=f"api/ideas/my/",
            related_object=idea
        )

        return idea

    # ----------------------------------------

    @staticmethod
    def reject_idea(*, idea, message):

        EvaluationDecisionService._validate_decision(idea, message)

        idea.status = IdeaStatus.REJECTED
        idea.save(update_fields=["status"])
        EvaluationDecisionService._try_finish_evaluation_phase(idea.season)

        NotificationService.send(
            user=idea.owner,
            title="تم رفض فكرتك",
            message=message,
            action_type="VIEW_IDEA",
            action_url=f"api/ideas/my/",
            related_object=idea
        )

        return idea
    
    
    





