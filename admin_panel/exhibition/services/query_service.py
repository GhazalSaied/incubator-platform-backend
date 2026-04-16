from django.core.exceptions import ValidationError

from ideas.models import ExhibitionSubmission


class ExhibitionQueryService:

    # =========================
    # FORM PREVIEW
    # =========================
    @staticmethod
    def get_form_preview(form):

        if not form:
            raise ValidationError("Form not found")

        questions = form.questions.all().order_by("order")

        return {
            "id": form.id,
            "title": form.title,
            "is_active": getattr(form, "is_active", False),

            # 🔥 مهم للـ frontend
            "mode": "preview",

            "questions": [
                ExhibitionQueryService._serialize_question(q)
                for q in questions
            ]
        }

    # =========================
    # QUESTION SERIALIZER
    # =========================
    @staticmethod
    def _serialize_question(question):

        return {
            "id": question.id,
            "key": question.key,
            "label": question.label,
            "type": question.type,
            "required": question.required,
            "order": question.order,

            # 🔥 مهم جداً للـ frontend rendering
            "component": ExhibitionQueryService._map_component(question.type),

            # options only if needed
            "options": ExhibitionQueryService._serialize_options(question)
        }

    # =========================
    # OPTIONS SERIALIZER
    # =========================
    @staticmethod
    def _serialize_options(question):

        if question.type not in ["select", "select_multiple", "radio"]:
            return []

        return [
            {
                "id": opt.id,
                "value": opt.value,
                "label": opt.label
            }
            for opt in question.options.all()
        ]

    # =========================
    # UI MAPPING (VERY IMPORTANT 🔥)
    # =========================
    @staticmethod
    def _map_component(q_type):

        mapping = {
            "text": "TextInput",
            "textarea": "TextArea",
            "number": "NumberInput",
            "email": "EmailInput",
            "select": "Select",
            "select_multiple": "MultiSelect",
            "radio": "RadioGroup",
            "checkbox": "Checkbox",
            "date": "DatePicker",
            "file": "FileUpload"
        }

        return mapping.get(q_type, "TextInput")
    
    
    
class ExhibitionSubmissionQueryService:

    @staticmethod
    def list_submissions():

        submissions = ExhibitionSubmission.objects.select_related(
            "project__owner"
        ).all().order_by("-created_at")

        return [
            {
                "id": s.id,
                "project_name": s.project.title,

                "owner_name": s.project.owner.full_name,

                "owner_image": (
                    s.project.owner.avatar.url
                    if s.project.owner.avatar else None
                ),

                "status": s.status
            }
            for s in submissions
        ]
        
        
    

    @staticmethod
    def get_submission_details(submission):

        project = submission.project
        form = submission.form

        questions = form.questions.all().order_by("order")

        answers = submission.data or {}

        return {
            # =========================
            # PROJECT INFO
            # =========================
            "project": {
                "name": project.title,
                "image": project.exhibition_image.url if project.exhibition_image else None,
                "owner_name": project.owner.full_name,
            },

            # =========================
            # FORM + ANSWERS
            # =========================
            "fields": [
                {
                    "label": q.label,
                    "type": q.type,
                    "answer": ExhibitionSubmissionQueryService._format_answer(
                        q,
                        answers.get(q.key)
                    )
                }
                for q in questions
            ],

            "status": submission.status
        }

    # =========================
    # FORMAT ANSWER (🔥 مهم)
    # =========================
    @staticmethod
    def _format_answer(question, value):

        if value is None:
            return None

        # select → رجع label بدل value
        if question.type in ["select", "radio"]:
            option = question.options.filter(value=value).first()
            return option.label if option else value

        # multiple select
        if question.type == "select_multiple":
            options = question.options.filter(value__in=value)
            return [opt.label for opt in options]

        return value