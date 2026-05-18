from django.db import transaction

from ideas.models import (
    IdeaForm,
    FormStep,
    FormQuestion,
    FormQuestionChoice,
    SeasonStatus
)


class FormBuilderService:

    # =====================================================
    # MAIN ENTRY
    # =====================================================

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

    # =====================================================
    # VALIDATE
    # =====================================================

    @staticmethod
    def _validate_editable(season):

        if season.status != SeasonStatus.DRAFT:
            raise Exception(
                "لا يمكن تعديل الفورم بعد نشر الموسم"
            )

    # =====================================================
    # STEP SYNC
    # =====================================================

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

            # UPDATE
            if step_id:

                step = FormStep.objects.get(
                    id=step_id,
                    form=form
                )

                for field, value in step_data.items():
                    setattr(step, field, value)

                step.save()

            # CREATE
            else:

                step = FormStep.objects.create(
                    form=form,
                    **step_data
                )

            kept_step_ids.append(step.id)

            FormBuilderService._sync_questions(
                form=form,
                step=step,
                questions_data=questions_data
            )

        # DELETE REMOVED STEPS
        FormStep.objects.filter(
            form=form
        ).exclude(
            id__in=kept_step_ids
        ).delete()

    # =====================================================
    # QUESTION SYNC
    # =====================================================

    @staticmethod
    def _sync_questions(
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

            # UPDATE
            if question_id:

                question = FormQuestion.objects.get(
                    id=question_id,
                    step=step
                )

                for field, value in question_data.items():
                    setattr(question, field, value)

                question.save()

            # CREATE
            else:

                question = FormQuestion.objects.create(
                    form=form,
                    step=step,
                    **question_data
                )

            kept_question_ids.append(
                question.id
            )

            FormBuilderService._sync_choices(
                question=question,
                choices_data=choices_data
            )

        # DELETE REMOVED QUESTIONS
        FormQuestion.objects.filter(
            step=step
        ).exclude(
            id__in=kept_question_ids
        ).delete()

    # =====================================================
    # CHOICES SYNC
    # =====================================================

    @staticmethod
    def _sync_choices(
        question,
        choices_data
    ):

        kept_choice_ids = []

        for choice_data in choices_data:

            choice_id = choice_data.pop(
                "id",
                None
            )

            # UPDATE
            if choice_id:

                choice = FormQuestionChoice.objects.get(
                    id=choice_id,
                    question=question
                )

                for field, value in choice_data.items():
                    setattr(choice, field, value)

                choice.save()

            # CREATE
            else:

                choice = FormQuestionChoice.objects.create(
                    question=question,
                    **choice_data
                )

            kept_choice_ids.append(
                choice.id
            )

        # DELETE REMOVED CHOICES
        FormQuestionChoice.objects.filter(
            question=question
        ).exclude(
            id__in=kept_choice_ids
        ).delete()