from cmath import phase

from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime

from ideas.models import Season
from ideas.phases import SeasonPhase as PhaseEnum
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase
from django.db import transaction
from ideas.models import ExhibitionForm, ExhibitionQuestion, ExhibitionQuestionOption


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

    @staticmethod
    def _validate_phase(season):
        phase = SeasonPhaseService.get_current_phase(season)

        if not phase:
            raise ValidationError("لا يوجد مرحلة حالية")

        if phase.phase != PhaseEnum.INCUBATION:
            raise ValidationError("لا يمكن انشاء المعرض في هذه المرحلة ")

        return phase

    @staticmethod
    def _get_next_order(season):
        last_phase = PhaseEnum.objects.filter(
            season=season
        ).order_by("-order").first()

        return last_phase.order + 1 if last_phase else 1
    @transaction.atomic
    @staticmethod
    def create_exhibition(*, date, time):

        # 🟢 1. parse datetime
        dt = ExhibitionAdminService._parse_datetime(date, time)

        # 🟢 2. get season
        season = ExhibitionAdminService._get_active_season()

        # 🟢 3. validate phase
        current_phase = ExhibitionAdminService._validate_phase(season)

        # 🛑 منع تكرار المعرض
        if season.exhibition_datetime:
            raise ValidationError("تم تحديد المعرض مسبقاً")

        # 🟢 4. حساب order
        new_order = ExhibitionAdminService._get_next_order(season)

        # 🟢 5. حفظ التاريخ
        season.exhibition_datetime = dt
        season.save()

        # 🟢 إنهاء المرحلة الحالية
        current_phase.end_date = timezone.now()
        current_phase.save()

# 🟢 جلب مرحلة المعرض
        exhibition_phase = SeasonPhase.objects.filter(
            season=season,
            phase=PhaseEnum.EXHIBITION
        ).first()

        if not exhibition_phase:
            raise ValidationError("مرحلة المعرض غير موجودة مسبقاً")

# 🟢 تفعيلها
        exhibition_phase.start_date = timezone.now()
        exhibition_phase.end_date = season.end_date
        exhibition_phase.save()

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

                # 🔥 check DB duplicate key (exclude self)
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

                # 🔥 DB check before create
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
        

        # ❗ if not selectable type → remove all options
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
    # 🔒 CHECK LOCK
    # =========================
    @staticmethod
    def check_not_published(form):
        if form.is_active:
            raise ValidationError("لا يمكن التعديل على بطاقة منشورة")

    # =========================
    # 🚀 PUBLISH FORM
    # =========================
    @staticmethod
    def publish_form(form):

        # 🔒 إذا منشور مسبقاً
        if form.is_active:
            raise ValidationError("الفورم منشور مسبقاً")

        # 🟢 تحقق من الموسم
        season = SeasonPhaseService.get_current_season()
        if not season:
            raise ValidationError("لا يوجد موسم فعال")

        # 🟢 تحقق من المرحلة
        phase = SeasonPhaseService.get_current_phase(season)
        if not phase or phase.phase != PhaseEnum.EXHIBITION:
            raise ValidationError("لا يمكن النشر إلا في مرحلة المعرض")

        # 🟢 تحقق انه الفورم فيه أسئلة
        if not form.questions.exists():
            raise ValidationError("لا يمكن نشر فورم فارغ")

        # 🟢 نشر
        form.is_active = True
        form.save()

        return form