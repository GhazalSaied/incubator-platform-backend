from ideas.models import IdeaForm, FormQuestion


class IdeaFormValidator:

    def __init__(self, form: IdeaForm, answers: dict):
        self.form = form
        self.answers = answers
        self.errors = {}

    def validate(self):
        questions = self.form.questions.all()

        for question in questions:
            key = question.key

            # Required check
            if question.required and key not in self.answers:
                self.errors[key] = "هذا الحقل مطلوب"
                continue

            if key not in self.answers:
                continue

            value = self.answers[key]

            # Type validation
            if question.type == FormQuestion.TEXT and not isinstance(value, str):
                self.errors[key] = "يجب أن يكون نصاً"

            elif question.type == FormQuestion.NUMBER and not isinstance(value, (int, float)):
                self.errors[key] = "يجب أن يكون رقماً"

            elif question.type == FormQuestion.BOOLEAN and not isinstance(value, bool):
                self.errors[key] = "يجب أن يكون نعم / لا"

            elif question.type == FormQuestion.SELECT and not isinstance(value, str):
                self.errors[key] = "قيمة غير صالحة"

        if self.errors:
            raise ValueError(self.errors)
