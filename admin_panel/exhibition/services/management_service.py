from cmath import phase
from core.events import EventBus
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime

from ideas.models import Season
from ideas.phases import SeasonPhase as PhaseEnum
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase
from django.db import transaction
from ideas.models import ExhibitionForm, ExhibitionQuestion, ExhibitionQuestionOption, ExhibitionSubmission


class ExhibitionAdminService:
    
    @staticmethod
    def _parse_datetime(date, time):
        if not date or not time:
            raise ValidationError("التاريخ والوقت مطلوبان")

        try:
            dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValidationError("تنسيق غير صحيح")

        dt = timezone.make_aware(dt)

        if dt < timezone.now():
            raise ValidationError("لا يمكن تحديد موعد في الماضي")

        return dt

    @staticmethod
    def _get_active_season():
        season = SeasonPhaseService.get_current_season()

        if not season:
            raise ValidationError("لا يوجد موسم فعال")

        return season


    @transaction.atomic
    @staticmethod
    def create_exhibition(*, date, time):

        #  1. parse datetime
        dt = ExhibitionAdminService._parse_datetime(date, time)

        #  2. get season
        season = ExhibitionAdminService._get_active_season()

        #  منع تكرار المعرض
        if season.exhibition_datetime:
            raise ValidationError("تم تحديد المعرض مسبقاً")

        #  5. حفظ التاريخ
        season.exhibition_datetime = dt
        season.save()
        EventBus.emit("exhibition_scheduled", season_id=season.id, exhibition_datetime=season.exhibition_datetime)

        return season


    # =========================
    # FORM
    # =========================

    @staticmethod
    def create_form(*, title):

        season = SeasonPhaseService.get_current_season()
        if not season:
            raise ValidationError("لا يوجد موسم فعال")

        if hasattr(season, "exhibition_form"):
            raise ValidationError("الفورم موجود مسبقاً")

        form = ExhibitionForm.objects.create(
            season=season,
            title=title,
            is_active=False
        )

        return form


    @staticmethod
    @transaction.atomic
    def sync_form(form, questions_data):
        ExhibitionAdminService.check_not_published(form)
        # =========================
        # VALIDATION (REQUEST LEVEL)
        # =========================
        incoming_keys = set()

        for q in questions_data:
            key = q.get("key")

            if not key:
                raise ValidationError("كل سؤال لازم يكون له key")

            if key in incoming_keys:
                raise ValidationError(f"Duplicate key in request: {key}")

            incoming_keys.add(key)

        # =========================
        # EXISTING DATA
        # =========================
        existing_questions = {
            q.id: q for q in form.questions.all()
        }

        incoming_ids = set()

        # =========================
        # SYNC QUESTIONS
        # =========================
        for q_data in questions_data:

            q_id = q_data.get("id")
            key = q_data["key"]

            # =========================
            # UPDATE QUESTION
            # =========================
            if q_id and q_id in existing_questions:

                question = existing_questions[q_id]

                #  check DB duplicate key (exclude self)
                if form.questions.exclude(id=q_id).filter(key=key).exists():
                    raise ValidationError(f"Key already exists: {key}")

                question.key = key
                question.label = q_data["label"]
                question.type = q_data["type"]
                question.required = q_data.get("required", False)
                question.order = q_data.get("order", 0)
                question.save()

                # sync options
                ExhibitionAdminService._sync_options(
                    question,
                    q_data.get("options", [])
                )

                incoming_ids.add(q_id)

            # =========================
            # CREATE QUESTION
            # =========================
            else:

                #  DB check before create
                if form.questions.filter(key=key).exists():
                    raise ValidationError(f"Key already exists: {key}")

                question = form.questions.create(
                    key=key,
                    label=q_data["label"],
                    type=q_data["type"],
                    required=q_data.get("required", False),
                    order=q_data.get("order", 0)
                )

                ExhibitionAdminService._sync_options(
                    question,
                    q_data.get("options", [])
                )

                incoming_ids.add(question.id)

        # =========================
        # DELETE REMOVED QUESTIONS
        # =========================
        to_delete = set(existing_questions.keys()) - incoming_ids

        if to_delete:
            form.questions.filter(id__in=to_delete).delete()

        return True

    # ==================================================
    # OPTIONS SYNC
    # ==================================================
    @staticmethod
    def _sync_options(question, options_data):
        

        if question.type not in ["select", "select_multiple"]:
            question.options.all().delete()
            return

        existing_options = {
            o.id: o for o in question.options.all()
        }

        incoming_ids = set()
        incoming_values = set()

        # =========================
        # VALIDATION (duplicate values)
        # =========================
        for opt in options_data:
            value = opt.get("value")

            if not value:
                raise ValidationError("كل خيار لازم يكون له value")

            if value in incoming_values:
                raise ValidationError(f"Duplicate option value: {value}")

            incoming_values.add(value)

        # =========================
        # SYNC OPTIONS
        # =========================
        for opt in options_data:

            opt_id = opt.get("id")
            value = opt["value"]

            # UPDATE OPTION
            if opt_id and opt_id in existing_options:

                option = existing_options[opt_id]

                option.value = value
                option.label = opt["label"]
                option.save()

                incoming_ids.add(opt_id)

            # CREATE OPTION
            else:

                new_opt = question.options.create(
                    value=value,
                    label=opt["label"]
                )

                incoming_ids.add(new_opt.id)

        # =========================
        # DELETE REMOVED OPTIONS
        # =========================
        to_delete = set(existing_options.keys()) - incoming_ids

        if to_delete:
            question.options.filter(id__in=to_delete).delete()


    # =========================
    #  CHECK LOCK
    # =========================
    @staticmethod
    def check_not_published(form):
        if form.is_active:
            raise ValidationError("لا يمكن التعديل على بطاقة منشورة")

    # =========================
    #  PUBLISH FORM
    # =========================
    @transaction.atomic
    @staticmethod
    def publish_form(form):

        #  إذا منشور مسبقاً
        if form.is_active:
            raise ValidationError("الفورم منشور مسبقاً")

    
        #  تحقق انه الفورم فيه أسئلة
        if not form.questions.exists():
            raise ValidationError("لا يمكن نشر فورم فارغ")

        #  نشر
        form.is_active = True
        form.save()
        EventBus.emit("exhibition_form_published", form_id=form.id, season_id=form.season.id)

        return form
    
    
    


class ExhibitionSubmissionManagementService:

    ALLOWED_DECISIONS = [
        "approved",
        "rejected"
    ]

    @staticmethod
    @transaction.atomic
    def process_decision(
        *,
        submission_id,
        decision,
        admin_message=None,
        actor=None
    ):

        submission = (
            ExhibitionSubmission.objects
            .select_for_update()
            .select_related("project", "project__owner")
            .get(id=submission_id)
        )

        # =========================
        # VALIDATION
        # =========================

        if submission.status != "pending":
            raise ValidationError(
                "تمت معالجة الطلب مسبقاً"
            )

        if decision not in (
            ExhibitionSubmissionManagementService
            .ALLOWED_DECISIONS
        ):
            raise ValidationError(
                "قرار غير صالح"
            )

        # تنظيف الرسالة
        admin_message = (
            admin_message.strip()
            if admin_message
            else None
        )

        # =========================
        # APPLY DECISION
        # =========================

        submission.status = decision
        submission.message = admin_message
        submission.reviewed_at = timezone.now()

        submission.save(
            update_fields=[
                "status",
                "message",
                "reviewed_at"
            ]
        )

        # =========================
        # EVENT
        # =========================

        EventBus.emit(
            "exhibition_submission_decided",
            submission=submission,
            decision=decision,
            message=admin_message,
            actor=actor
        )

        return submission