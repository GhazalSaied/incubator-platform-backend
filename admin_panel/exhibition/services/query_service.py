import re

from django.core.exceptions import ValidationError

from core import settings
from ideas.models import ExhibitionSubmission, IdeaStatus, Season


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
    # UI MAPPING (VERY IMPORTANT )
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

        questions = form.questions.all()

        answers = submission.data or {}

    # -------------------------
    # helper للبحث عن جواب سؤال
    # -------------------------
        def get_answer_by_label(label):
            
            def normalize(text):
                text = str(text).strip()
                text = text.replace("-", " ")
                text = text.replace("_", " ")
                text = re.sub(r"\s+", " ", text)
                return text
                    
                
            target = normalize(label)

            for key, value in answers.items():
            

                if normalize(key) == target:
                    return value


            return None
        # ==========================
        # get uploaded image answer
        # ==========================
        
                          
        return {
            "id": submission.id,

            "owner_name": (
                project.owner.full_name
                if project.owner
                    else None
                ),
            "project_image": ( f"/media/{get_answer_by_label('صورة-المشروع')}"
                if get_answer_by_label("صورة-المشروع")

                else None
),
        

            "owner_email": (
                project.owner.email
                if project.owner
                else None
            ),

            "title": project.title,

            "sector": project.sector,


            "team_members": [
                member.user.full_name
                for member in project.team_members.all()
            ],

    # ======================
    # goal from form
    # ======================
            "project_goal": get_answer_by_label("اهداف-المشروع"),
                

    # ======================
    # services from form
    # ======================
            "project_services": get_answer_by_label("خدمات المشروع"),
                
            "emails": [
                member.user.email
                for member in project.team_members.all()
                if member.user.email
            ],

            "owner_id": (
                project.owner.id
                if project.owner
                else None
            ),

            "status": submission.status
}
    
    # =========================
    # FORMAT ANSWER ( مهم)
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
    
    
class ExhibitionHistoryQueryService:

    @staticmethod
    def list_exhibitions(year=None):

        seasons = Season.objects.exclude(
            exhibition_datetime=None
        )

        #  فلترة حسب السنة إذا موجودة
        if year:
            seasons = seasons.filter(
                exhibition_datetime__year=year
            )

        seasons = seasons.order_by("-exhibition_datetime")

        data = []

        for season in seasons:

            projects_count = season.ideas.filter(
                status=IdeaStatus.GRADUATED_POSITIVE
            ).count()

            data.append({
                "id": season.id,
                "title": f"معرض خريجين {season.name}",
                "date": season.exhibition_datetime.strftime("%d/%m/%Y"),

                "year": season.exhibition_datetime.year,

                "projects_count": projects_count
            })

        return data


    @staticmethod
    def get_exhibition_projects(season, search=None, sector=None):

        submissions = ExhibitionSubmission.objects.filter(
            project__season=season,
            project__status="GRADUATED_POSITIVE"
        ).select_related(
            "project__owner"
        ).prefetch_related(
            "project__team_members__user"
        )

        #  search
        if search:
            submissions = submissions.filter(
                project__title__icontains=search
            )

        #  filter
        if sector:
            submissions = submissions.filter(
                project__sector__iexact=sector
            )

        return [
            {
                
                "submission_id": s.id, 
                "year": season.exhibition_datetime.year,

                "title": s.project.title,
                "category": s.project.sector,

                "owner_name": s.project.owner.full_name,

                "team_members": [
                    member.user.full_name
                    for member in s.project.team_members.all()
                ]
            }
            for s in submissions
        ]