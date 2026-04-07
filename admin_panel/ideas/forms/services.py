
from django.db import transaction
from django.core.exceptions import ValidationError
from ideas.models import Idea,Season,IdeaForm,FormQuestion,FormQuestionChoice

class FormBuilderService:
    @staticmethod
    def create_form(season, data):
        return IdeaForm.objects.create(
            season=season,
            title=data.get("title", "نموذج التقديم")
        )
    @staticmethod
    def _validate_questions(questions_data):

    # 🟢 duplicate keys
        keys = [q.get("key") for q in questions_data]
        if len(keys) != len(set(keys)):
            raise ValidationError("يوجد مفاتيح مكررة للأسئلة")

        for q in questions_data:

            q_type = q.get("type")
            choices = q.get("choices", [])

        # 🟡 select لازم choices
            if q_type in ["select", "select_multiple"]:

                if not choices:
                    raise ValidationError(
                        f"السؤال '{q.get('label')}' يحتاج خيارات"
                    )

            # 🔵 duplicate choice values
                values = [c.get("value") for c in choices]

                if len(values) != len(set(values)):
                    raise ValidationError(
                        f"السؤال '{q.get('label')}' يحتوي قيم مكررة"
                    )

        # 🟣 non-select ما لازم choices
            else:
                if choices:
                    raise ValidationError(
                        f"السؤال '{q.get('label')}' لا يجب أن يحتوي خيارات"
                    )

    @staticmethod
    def save_form_builder(form, questions_data):

        if form.season.phases.exists():
            raise ValidationError("لا يمكن التعديل بعد نشر الموسم")
        # 🔥 VALIDATION
        FormBuilderService._validate_questions(questions_data)

        existing_questions = {q.id: q for q in form.questions.all()}
        sent_ids = []

        for q_data in questions_data:

            q_id = q_data.get("id")

            # 🟩 UPDATE
            if q_id and q_id in existing_questions:
                question = existing_questions[q_id]

                question.label = q_data.get("label", question.label)
                question.type = q_data.get("type", question.type)
                question.required = q_data.get("required", question.required)
                question.order = q_data.get("order", question.order)
                question.key = q_data.get("key", question.key)

                question.save()
                sent_ids.append(q_id)

            # 🟦 CREATE
            else:
                question = FormQuestion.objects.create(
                    form=form,
                    key=q_data.get("key"),
                    label=q_data.get("label"),
                    type=q_data.get("type"),
                    required=q_data.get("required", False),
                    order=q_data.get("order", 0),
                )

                sent_ids.append(question.id)

            # 🟪 CHOICES
            FormBuilderService._handle_choices(
                question,
                q_data.get("choices", [])
            )

        # 🟥 DELETE QUESTIONS
        for q_id, question in existing_questions.items():
            if q_id not in sent_ids:
                question.delete()

    # -------------------------

    @staticmethod
    def _handle_choices(question, choices_data):

        existing_choices = {c.id: c for c in question.choices.all()}
        sent_ids = []

        for c_data in choices_data:

            c_id = c_data.get("id")

            # UPDATE
            if c_id and c_id in existing_choices:
                choice = existing_choices[c_id]

                choice.value = c_data.get("value", choice.value)
                choice.label = c_data.get("label", choice.label)
                choice.order = c_data.get("order", choice.order)

                choice.save()
                sent_ids.append(c_id)

            # CREATE
            else:
                choice = FormQuestionChoice.objects.create(
                    question=question,
                    value=c_data["value"],
                    label=c_data["label"],
                    order=c_data.get("order", 0)
                )

                sent_ids.append(choice.id)

        # DELETE
        for c_id, choice in existing_choices.items():
            if c_id not in sent_ids:
                choice.delete()
                
    @staticmethod
    def get_form_preview(form):

        questions = form.questions.prefetch_related("choices").order_by("order")

        result = []

        for q in questions:

            result.append({
                "id": q.id,
                "key": q.key,
                "label": q.label,
                "type": q.type,
                "required": q.required,
                "order": q.order,
                "choices": [
                    {
                        "id": c.id,
                        "value": c.value,
                        "label": c.label,
                        "order": c.order
                    }
                    for c in q.choices.all().order_by("order")
                ]
            })

        return result
