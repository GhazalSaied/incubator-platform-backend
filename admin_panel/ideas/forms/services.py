
from django.db import transaction
from rest_framework.exceptions import ValidationError

from ideas.models import (
    IdeaForm,
    FormStep,
    FormQuestion,
    FormQuestionChoice,
    Season,
    SeasonStatus
)

 

class FormBuilderService:

    # ==========================================
    # STATIC QUESTIONS CONFIG
    # ==========================================

    STATIC_QUESTIONS = {
        "title": {
            "key": "title",
            "label": "عنوان الفكرة",
            "type": FormQuestion.TEXT,
        },

        "description": {
            "key": "description",
            "label": "وصف الفكرة",
            "type": FormQuestion.TEXT,
        },

        "target_audience": {
            "key": "target_audience",
            "label": "الفئة المستهدفة",
            "type": FormQuestion.TEXT,
        },

        "sector": {
            "key": "sector",
            "label": "القطاع",
            "type": FormQuestion.TEXT,
        },
    }

    # ==========================================
    # MAIN
    # ==========================================

    @staticmethod
    @transaction.atomic
    def sync(season, data):

        FormBuilderService._validate_editable(
            season
        )

        form, _ = IdeaForm.objects.get_or_create(
            season=season,
            defaults={
                "title": data["title"]
            }
        )

        form.title = data["title"]

        form.save(update_fields=["title"])

        FormBuilderService._sync_steps(
            form=form,
            steps_data=data.get("steps", [])
        )

        return form

    # ==========================================
    # VALIDATE
    # ==========================================

    @staticmethod
    def _validate_editable(season):

        if season.status != SeasonStatus.DRAFT:
            raise ValidationError(
                "لا يمكن تعديل الفورم بعد نشر الموسم"
            )

    # ==========================================
    # STEPS
    # ==========================================

    @staticmethod
    def _sync_steps(form, steps_data):

        kept_step_ids = []

        for step_data in steps_data:

            questions_data = step_data.pop(
                "questions",
                []
            )

            step_id = step_data.pop(
                "id",
                None
            )

            # ==========================
            # UPDATE STEP
            # ==========================

            if step_id:

                step = FormStep.objects.get(
                    id=step_id,
                    form=form
                )

                step.title = step_data["title"]
                step.order = step_data["order"]

                step.save()

            # ==========================
            # CREATE STEP
            # ==========================

            else:

                step = FormStep.objects.create(
                    form=form,
                    title=step_data["title"],
                    order=step_data["order"]
                )

            kept_step_ids.append(step.id)

            # ==========================
            # QUESTIONS
            # ==========================

            FormBuilderService._sync_questions(
                form=form,
                step=step,
                questions_data=questions_data
            )

        # ==========================
        # DELETE REMOVED STEPS
        # ==========================

        FormStep.objects.filter(
            form=form
        ).exclude(
            id__in=kept_step_ids
        ).delete()

    # ==========================================
    # QUESTIONS
    # ==========================================

    @staticmethod
    def _sync_questions(
        *,
        form,
        step,
        questions_data
    ):

        kept_question_ids = []

        for question_data in questions_data:

            choices_data = question_data.pop(
                "choices",
                []
            )

            question_id = question_data.pop(
                "id",
                None
            )

            is_static = question_data.pop(
                "is_static",
                False
            )

            # ======================================
            # STATIC QUESTION
            # ======================================

            if is_static:

                static_field = question_data["static_field"]

                if static_field not in (
                    FormBuilderService.STATIC_QUESTIONS
                ):
                    raise ValidationError(
                        "حقل static غير صالح"
                    )

                config = (
                    FormBuilderService
                    .STATIC_QUESTIONS[static_field]
                )

                question, _ = (
                    FormQuestion.objects.get_or_create(
                        form=form,
                        static_field=static_field,
                        defaults={
                            "step": step,
                            "source": FormQuestion.STATIC,
                            "key": config["key"],
                            "label": config["label"],
                            "type": config["type"],
                            "required": question_data.get(
                                "required",
                                False
                            ),
                            "order": question_data.get(
                                "order",
                                0
                            )
                        }
                    )
                )

                # move between steps
                question.step = step

                question.required = (
                    question_data.get(
                        "required",
                        False
                    )
                )

                question.order = (
                    question_data.get(
                        "order",
                        0
                    )
                )

                question.save()

            # ======================================
            # DYNAMIC QUESTION
            # ======================================

            else:

                # UPDATE
                if question_id:

                    question = FormQuestion.objects.get(
                        id=question_id,
                        form=form
                    )

                    for field, value in (
                        question_data.items()
                    ):
                        setattr(
                            question,
                            field,
                            value
                        )

                    question.step = step

                    question.save()

                # CREATE
                else:
                    label = question_data.get("label")
                    question_data["key"] = label
                    question = (
                        FormQuestion.objects.create(
                            form=form,
                            step=step,
                            source=FormQuestion.DYNAMIC,
                            **question_data
                        )
                    )

            kept_question_ids.append(
                question.id
            )

            # ======================================
            # CHOICES
            # ======================================

            FormBuilderService._sync_choices(
                question=question,
                choices_data=choices_data
            )

        # ======================================
        # DELETE REMOVED QUESTIONS
        # ======================================

        FormQuestion.objects.filter(
            form=form,
            step=step
        ).exclude(
            id__in=kept_question_ids
        ).delete()

    # ==========================================
    # CHOICES
    # ==========================================

    @staticmethod
    def _sync_choices(
        *,
        question,
        choices_data
    ):

        kept_choice_ids = []

        for choice_data in choices_data:

            choice_id = choice_data.pop(
                "id",
                None
            )

            # ==========================
            # UPDATE
            # ==========================

            if choice_id:

                choice = (
                    FormQuestionChoice.objects.get(
                        id=choice_id,
                        question=question
                    )
                )

                for field, value in (
                    choice_data.items()
                ):
                    setattr(
                        choice,
                        field,
                        value
                    )

                choice.save()

            # ==========================
            # CREATE
            # ==========================

            else:

                choice = (
                    FormQuestionChoice.objects.create(
                        question=question,
                        **choice_data
                    )
                )

            kept_choice_ids.append(
                choice.id
            )

        # ==========================
        # DELETE REMOVED CHOICES
        # ==========================

        FormQuestionChoice.objects.filter(
            question=question
        ).exclude(
            id__in=kept_choice_ids
        ).delete()