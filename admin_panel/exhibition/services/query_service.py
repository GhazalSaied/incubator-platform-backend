from django.core.exceptions import ValidationError


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