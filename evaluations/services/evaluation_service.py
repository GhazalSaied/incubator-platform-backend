from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.events import EventBus
from django.shortcuts import get_object_or_404

from evaluations.models import (
    Evaluation,
    EvaluationScore,
    EvaluationAssignment,
    IncubationAssignment,
    EvaluationCriterion,
    EvaluationNote,
    EvaluationSettings,
    IncubationReview,
    
    
)

from ideas.services.season_phase_service import SeasonPhaseService
from ideas.models import Idea,IdeaStatus
from ideas.services.idea_service import IdeaService
from django.db.models import Max
from django.db.models.functions import TruncDate
from django.utils import timezone

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


        scores_data = data.get("scores", [])

        for score_data in scores_data:
            criterion = EvaluationCriterion.objects.get(
                id=score_data["criterion"]
            )

            score_value = score_data.get("score")

            if score_value is None:
                raise ValidationError("الدرجة مطلوبة")

            if score_value < 0:
                raise ValidationError("الحد الأدنى للدرجة هو 0")

            if score_value > criterion.max_score:
                raise ValidationError("الدرجة تتجاوز الحد الأعلى")

            EvaluationScore.objects.update_or_create(
                evaluation=evaluation,
                criterion=criterion,
                defaults={
                    "score": score_value
                }
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

        EventBus.emit(
            "evaluation_submitted", 
            evaluation= evaluation,
            idea= idea,
            user= user,
        )

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
        """
        Unified evaluator assignments source:

        - EVALUATION phase  -> EvaluationAssignment
        - INCUBATION phase -> IncubationAssignment

        Response match Evaluation Center UI only.
        """

        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            return []

        # =====================================
        # EVALUATION PHASE
        # =====================================

        if phase.phase == "EVALUATION":
            assignments = EvaluationAssignment.objects.filter(
                evaluator=user,
                season=season
            ).select_related("idea")

            return [
                {
                    "id": assignment.id,
                    "idea_id": assignment.idea.id,
                    "title": assignment.idea.title,
                    "product_type": assignment.idea.answers.get("نوع المنتج"),
                    "target_audience": assignment.idea.target_audience,
                }
                for assignment in assignments
            ]

        # =====================================
        # INCUBATION PHASE
        # =====================================

        if phase.phase == "INCUBATION":
            assignments = IncubationAssignment.objects.filter(
                mentor__user=user,
                idea__season=season
            ).select_related("idea", "mentor")

            return [
                {
                    "id": assignment.id,
                    "idea_id": assignment.idea.id,
                    "title": assignment.idea.title,
                    "product_type": assignment.idea.answers.get("نوع المنتج"),
                    "target_audience": assignment.idea.target_audience,
                }
                for assignment in assignments
            ]

        return []


    # ////////////////////////////////// ASSIGNMENT DETAIL //////////////////////////////////



    @staticmethod
    def get_assignment_detail(user, assignment_id):
        """
        Resolve assignment details based on current season phase.

        - EVALUATION  -> EvaluationAssignment.meeting_date
        - INCUBATION -> IncubationAssignment.meeting_date

        Returns:
        {
            meeting_date,
            idea
        }
        """

        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            raise ValidationError("لا يوجد موسم أو مرحلة حالية")

        # =====================================
        # EVALUATION PHASE
        # =====================================

        if phase.phase == "EVALUATION":
            assignment = get_object_or_404(
                EvaluationAssignment.objects.select_related(
                    "idea",
                    "idea__owner"
                ),
                id=assignment_id,
                evaluator=user,
                season=season
            )

            return {
                "meeting_date": assignment.meeting_date,
                "idea": assignment.idea,
            }

        # =====================================
        # INCUBATION PHASE
        # =====================================

        if phase.phase == "INCUBATION":
            assignment = get_object_or_404(
                IncubationAssignment.objects.select_related(
                    "idea",
                    "idea__owner",
                    "mentor"
                ),
                id=assignment_id,
                mentor__user=user,
                idea__season=season
            )

            return {
                "meeting_date": assignment.meeting_date,
                "idea": assignment.idea,
            }

        raise ValidationError("مرحلة غير مدعومة")

    


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

    #/////////////////////// OPEN EVALUATION FORM //////////////////

    @staticmethod
    def get_evaluation_form(user, idea):
        """
        Evaluation phase only.

        Returns:
        - form published state
        - active criteria
        - existing saved scores
        - submitted state
        """

        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            raise ValidationError("لا يوجد موسم أو مرحلة حالية")

        if phase.phase != "EVALUATION":
            raise ValidationError("نموذج التقييم متاح فقط في مرحلة التقييم")

        assignment = EvaluationAssignment.objects.filter(
            evaluator=user,
            idea=idea,
            season=season
        ).first()

        if not assignment:
            raise ValidationError("غير مصرح لك بتقييم هذه الفكرة")

        settings = EvaluationSettings.objects.order_by("-created_at").first()

        is_published = settings.is_published if settings else False

        if not is_published:
            return {
                "is_published": False,
                "criteria": [],
                "scores": [],
                "is_submitted": False,
            }

        evaluation, _ = Evaluation.objects.get_or_create(
            evaluator=user,
            idea=idea,
            season=season
        )

        criteria = EvaluationCriterion.objects.filter(
            is_active=True
        ).order_by("order")

        existing_scores = {
            score.criterion_id: score.score
            for score in evaluation.scores.all()
        }

        criteria_data = []
        scores_data = []

        for criterion in criteria:
            criteria_data.append({
                "id": criterion.id,
                "title": criterion.title,
                "max_score": criterion.max_score,
            })

            scores_data.append({
                "criterion": criterion.id,
                "score": existing_scores.get(criterion.id),
        })
        return {
            "is_published": True,
            "criteria": criteria_data,
            "scores": scores_data,
            "is_submitted": evaluation.is_submitted,
        }


#///////////////////////// NOTES (ADD AND GET ) //////////////////////


    @staticmethod
    def add_evaluation_note(user, idea, note_text):
        evaluation = get_object_or_404(
            Evaluation,
            evaluator=user,
            idea=idea
        )

        return EvaluationNote.objects.create(
            evaluation=evaluation,
            note=note_text
        )

    @staticmethod
    def get_evaluation_notes(user, idea):
        evaluation = get_object_or_404(
            Evaluation,
            evaluator=user,
            idea=idea
        )

        return evaluation.evaluation_notes.all()


#////////////////////////// CREATE INCUBATION REVIEW (NEW ROW PER SESSION) ///////////////////////


    @staticmethod
    def create_incubation_review(user, idea, data):
        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            raise ValidationError("لا يوجد موسم أو مرحلة حالية")

        if phase.phase != "INCUBATION":
            raise ValidationError("المراجعات الدورية متاحة فقط في مرحلة الاحتضان")

        assignment = IncubationAssignment.objects.filter(
            mentor__user=user,
            idea=idea,
            idea__season=season
        ).first()

        if not assignment:
            raise ValidationError("غير مصرح لك بمراجعة هذا المشروع")

        progress_score = data.get("progress_score")
        notes = data.get("notes")

        if progress_score is None:
            raise ValidationError("نسبة التقدم مطلوبة")

        if progress_score < 0 or progress_score > 100:
            raise ValidationError("نسبة التقدم يجب أن تكون بين 0 و 100")

        if not notes:
            raise ValidationError("الملاحظات مطلوبة")
        

        review = IncubationReview.objects.create(
            idea=idea,
            progress_score=progress_score,
            notes=notes,
            created_by=user,
            is_submitted=True,
            submitted_at=timezone.now(),
        )

        return review

#//////////////////////////// PREVIOUS INCUBATION REVIEWS ///////////////////////


    @staticmethod
    def get_incubation_reviews(user, idea):
        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            raise ValidationError("لا يوجد موسم أو مرحلة حالية")

        if phase.phase != "INCUBATION":
            raise ValidationError("المراجعات الدورية متاحة فقط في مرحلة الاحتضان")

        assignment = IncubationAssignment.objects.filter(
            mentor__user=user,
            idea=idea,
            idea__season=season
        ).first()

        if not assignment:
            raise ValidationError("غير مصرح لك بمراجعة هذا المشروع")

        return IncubationReview.objects.filter(
            idea=idea,
            created_by=user
        ).order_by("-created_at").values(
            "id",
            "notes",
            "created_at"
        )
    

#/////////////////////////////// NEXT UPCOMING SESSION (PHASE-BASED) /////////////////


    @staticmethod
    def get_next_session(user):
        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            return None

        now = timezone.now()

        if phase.phase == "EVALUATION":
            next_assignment = EvaluationAssignment.objects.filter(
                evaluator=user,
                season=season,
                meeting_date__gte=now
            ).order_by("meeting_date").first()

            if not next_assignment:
                return None

            return {
                "meeting_date": next_assignment.meeting_date,
                "idea_title": next_assignment.idea.title,
                "phase": "EVALUATION",
            }

        if phase.phase == "INCUBATION":
            next_assignment = IncubationAssignment.objects.filter(
                mentor__user=user,
                idea__season=season,
                meeting_date__gte=now
            ).order_by("meeting_date").first()

            if not next_assignment:
                return None

            return {
                "meeting_date": next_assignment.meeting_date,
                "idea_title": next_assignment.idea.title,
                "phase": "INCUBATION",
            }

        return None
    
   
#///////////////////////// LATEST INCUBATION REVIEWS FOR ALL EVALUATORS ////////////////

    @staticmethod
    def get_latest_incubation_notes_for_incubatee(user, idea):

        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            raise ValidationError("لا يوجد موسم أو مرحلة حالية")

        if phase.phase != "INCUBATION":
            raise ValidationError(
                "المراجعات الدورية متاحة فقط في مرحلة الاحتضان"
            )


        latest_review_date = (
            IncubationReview.objects.filter(
                idea=idea,
                is_submitted=True,
                submitted_at__isnull=False,
            )
            .annotate(review_date=TruncDate("submitted_at"))
            .aggregate(latest_date=Max("review_date"))
            .get("latest_date")
        )

        if not latest_review_date:
            return IncubationReview.objects.none()

        return (
            IncubationReview.objects.filter(
                idea=idea,
                is_submitted=True,
                submitted_at__date=latest_review_date,
            )
            .only("notes", "submitted_at")
            .order_by("submitted_at")
        )
    

#/////////////////// INCUBATION PHASE > تاب مراحل الاحتضان  (NOTES + MEETING DATE )//////////////////////

    @staticmethod
    def get_incubation_overview_for_incubatee(
        *,
        user,
        idea,
    ):

        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(
            season
        )

        if not season or not phase:
            raise ValidationError(
                "لا يوجد موسم أو مرحلة حالية"
            )

        if phase.phase != "INCUBATION":
            raise ValidationError(
                "هذه البيانات متاحة فقط ضمن مرحلة الاحتضان"
            )

        next_meeting = (
            IncubationAssignment.objects.filter(
                idea=idea,
                meeting_date__isnull=False,
                meeting_date__gte=timezone.now(),
            )
            .order_by("meeting_date")
            .first()
        )

        latest_notes = (
            EvaluationService
            .get_latest_incubation_notes_for_incubatee(
                user=user,
                idea=idea
            )
        )

        return {
            "next_meeting_date": (
                next_meeting.meeting_date
                if next_meeting
                else None
            ),
            "notes": latest_notes,
        }
    
#////////////////// EVALUATION SESSION STATUS > مرحلة التقييم في تاب مراحل الاحتضان ////////////////

    @staticmethod
    def get_idea_evaluation_session_status(
        *,
        user,
        idea,
    ):

        is_owner = idea.owner == user

        is_team_member = idea.team_members.filter(
            user=user
        ).exists()

        if not is_owner and not is_team_member:
            raise ValidationError(
                "غير مصرح لك بعرض بيانات التقييم"
            )

        assignments = EvaluationAssignment.objects.filter(
            idea=idea
        )

        if not assignments.exists():
            raise ValidationError(
                "لا يوجد لجنة تقييم لهذه الفكرة"
        )

        assignment = assignments.first()

        meeting_date = assignment.meeting_date

        if not meeting_date:
            raise ValidationError(
                "لم يتم تحديد موعد جلسة التقييم بعد"
            )

        now = timezone.now()

        if now < meeting_date:
            evaluation_status = "PENDING"

        else:

            total_assignments = assignments.count()

            completed_assignments = assignments.filter(
                is_completed=True
            ).count()

            if completed_assignments == total_assignments:
                evaluation_status = "COMPLETED"
            else:
                evaluation_status = "IN_REVIEW"

        return {
            "meeting_date": meeting_date,
            "status": evaluation_status,
        }
    
    #//////////////////// REJECTED IDEA EVALUATION NOTES ////////////////////

    @staticmethod
    def get_rejected_idea_notes_for_owner(user, idea_id):

        idea = IdeaService.get_dashboard_idea(user)

        if idea.id != idea_id:
            raise ValidationError("لا تملك صلاحية الوصول لهذه الفكرة")

        if idea.status != IdeaStatus.REJECTED:
            raise ValidationError(
                "ملاحظات اللجنة متاحة فقط للأفكار المرفوضة"
            )

        return (
            EvaluationNote.objects
            .filter(
                evaluation__idea=idea,
                evaluation__is_submitted=True
            )
            .only(
                "note",
            )
            .order_by("-created_at")
        )