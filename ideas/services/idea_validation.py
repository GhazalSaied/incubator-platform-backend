from rest_framework.exceptions import ValidationError

from ideas.models import FormQuestion


class IdeaValidationService:

    STATIC_FIELDS = {
        "title",
        "description",
        "target_audience",
        "sector",
    }

    @classmethod
    def validate_step(cls, step, payload):

        validated_data = {}

        questions = step.questions.prefetch_related("choices").all()

        for question in questions:

            incoming_value = payload.get(question.key)

            if question.required and incoming_value in [None, "", []]:
                raise ValidationError({
                    question.key: "هذا الحقل مطلوب"
                })

            if incoming_value is None:
                continue

            validated_data[question.key] = cls._validate_question_value(
                question,
                incoming_value
            )

        return validated_data

    @classmethod
    def validate_full_submission(cls, form, idea):

        all_questions = form.questions.prefetch_related("choices").all()

        for question in all_questions:

            value = cls._extract_question_value(
                idea,
                question
            )

            if question.required and value in [None, "", []]:
                raise ValidationError({
                    question.key: "هذا الحقل مطلوب قبل الإرسال النهائي"
                })

            if value is not None:
                cls._validate_question_value(question, value)

    @classmethod
    def _extract_question_value(cls, idea, question):

        if question.source == FormQuestion.STATIC:
            return getattr(idea, question.static_field)

        return idea.answers.get(question.key)

    @classmethod
    def _validate_question_value(cls, question, value):

        if question.type == FormQuestion.TEXT:
            return cls._validate_text(value)

        if question.type == FormQuestion.NUMBER:
            return cls._validate_number(value)

        if question.type == FormQuestion.BOOLEAN:
            return cls._validate_boolean(value)

        if question.type == FormQuestion.SELECT:
            return cls._validate_select(question, value)

        if question.type == FormQuestion.SELECT_MULTIPLE:
            return cls._validate_select_multiple(question, value)

        if question.type == FormQuestion.LIST_TEXT:
            return cls._validate_list_text(value)

        raise ValidationError("نوع السؤال غير مدعوم")

    @staticmethod
    def _validate_text(value):

        if not isinstance(value, str):
            raise ValidationError("القيمة يجب أن تكون نص")

        return value.strip()

    @staticmethod
    def _validate_number(value):

        if not isinstance(value, int):
            raise ValidationError("القيمة يجب أن تكون رقم صحيح")

        return value

    @staticmethod
    def _validate_boolean(value):

        if not isinstance(value, bool):
            raise ValidationError("القيمة يجب أن تكون true/false")

        return value

    @staticmethod
    def _validate_list_text(value):

        if not isinstance(value, list):
            raise ValidationError("القيمة يجب أن تكون array")

        for item in value:
            if not isinstance(item, str):
                raise ValidationError("كل عناصر القائمة يجب أن تكون نصوص")

        return value

    @staticmethod
    def _validate_select(question, value):

        valid_values = set(
            question.choices.values_list("value", flat=True)
        )

        if value not in valid_values:
            raise ValidationError("الخيار غير صالح")

        return value

    @staticmethod
    def _validate_select_multiple(question, value):

        if not isinstance(value, list):
            raise ValidationError("القيمة يجب أن تكون قائمة")

        valid_values = set(
            question.choices.values_list("value", flat=True)
        )

        for item in value:
            if item not in valid_values:
                raise ValidationError("أحد الخيارات غير صالح")

        return value