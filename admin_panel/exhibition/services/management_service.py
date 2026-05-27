from cmath import phase
from core.events import EventBus
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.text import slugify
from ideas.models import Season
from ideas.phases import SeasonPhase as PhaseEnum
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase
from django.db import transaction
from ideas.models import ExhibitionForm, ExhibitionQuestion, ExhibitionQuestionOption, ExhibitionSubmission


class ExhibitionAdminService:
    FIELD_TYPES = {
        "short_text": "text",
        "long_text": "textarea",
        "single_choice": "select",
        "multiple_choice": "select_multiple",
        "yes_no": "yes_no",
    }

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
    @transaction.atomic
    def save_form(*, title, questions_data):

        season = SeasonPhaseService.get_current_season()

        if not season:
            raise ValidationError("لا يوجد موسم فعال")

        form, _ = ExhibitionForm.objects.get_or_create(
            season=season,
            defaults={
                "title": title,
                "is_active": False
            }
        )

        ExhibitionAdminService.check_not_published(form)

        form.title = title
        form.save()

        existing_questions = {
            q.id: q for q in form.questions.all()
        }

        incoming_ids = set()

        for index, q_data in enumerate(questions_data):

            q_id = q_data.get("id")

            ui_type = q_data.get("type")

            if ui_type not in ExhibitionAdminService.FIELD_TYPES:
                raise ValidationError("نوع الحقل غير صالح")

            db_type = ExhibitionAdminService.FIELD_TYPES[ui_type]

            label = q_data.get("label")

            if not label:
                raise ValidationError("عنوان السؤال مطلوب")

            required = q_data.get("required", False)

            # توليد key تلقائي
            key = slugify(label, allow_unicode=True)

            # yes/no options auto
            options = q_data.get("options", [])

            if ui_type == "yes_no":
                options = [
                    {"label": "نعم", "value": "yes"},
                    {"label": "لا", "value": "no"},
                ]

            # =========================
            # UPDATE
            # =========================
            if q_id and q_id in existing_questions:

                question = existing_questions[q_id]

                question.label = label
                question.type = db_type
                question.required = required
                question.order = index
                question.key = key
                question.save()

            # =========================
            # CREATE
            # =========================
            else:

                question = form.questions.create(
                    label=label,
                    type=db_type,
                    required=required,
                    order=index,
                    key=key,
                )

            ExhibitionAdminService._sync_options(
                question,
                options
            )

            incoming_ids.add(question.id)

        # حذف الأسئلة المحذوفة من الواجهة
        deleted_ids = (
            set(existing_questions.keys()) - incoming_ids
        )

        if deleted_ids:
            form.questions.filter(
                id__in=deleted_ids
            ).delete()

        return form

    @staticmethod
    def _sync_options(question, options):

        if question.type not in [
            "select",
            "select_multiple"
        ]:
            question.options.all().delete()
            return

        question.options.all().delete()

        for opt in options:

            label = opt.get("label")

            if not label:
                continue

            question.options.create(
                label=label,
                value=slugify(label)
            )

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