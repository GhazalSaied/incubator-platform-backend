from datetime import date
from django.db.models import Count
from ideas.models import Season, Idea, IdeaStatus, IdeaForm, FormQuestion, FormQuestionChoice
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase



class SeasonQueryService:


    # =============================
    
    @staticmethod
    def get_phase_name(season):
        phase_obj = SeasonPhaseService.get_current_phase(season)
        return phase_obj.phase if phase_obj else None

    @staticmethod
    def get_ideas_count(season):
        count = getattr(season, "ideas_count", None)
        return count if count is not None else season.ideas.count()

    @staticmethod
    def get_evaluation_ideas_count(season):
        return season.ideas.filter(
            status=IdeaStatus.EVALUATION
        ).count()

    @staticmethod
    def get_remaining_days(season):
        return max((season.end_date - date.today()).days, 0)
    # =============================
    # 🔹 Status (List Page)
    # =============================

    @staticmethod
    def get_season_status(season, phase_name):
        return {
            "is_open": season.is_open,
            "label": "مفتوح" if season.is_open else "مغلق",
            "phase": phase_name
        }

    @staticmethod
    def build_season_response(season):
        phase_name = SeasonQueryService.get_phase_name(season)
        
        return {
            "id": season.id,
            "year": season.start_date.year,
            "name": season.name,
            "start_date": season.start_date,
            "end_date": season.end_date,
            "ideas_count": getattr(season, "ideas_count", season.ideas.count()),
            "status": SeasonQueryService.get_season_status(
                season,
                phase_name
            )
        }

    @staticmethod
    def list_seasons():
        qs = Season.objects.all()

        return [
            SeasonQueryService.build_season_response(season)
            for season in qs
        ]

    # =============================
    # 🔹 Season Details Page
    # =============================

    @staticmethod
    def get_season_details(season, ordering=None):

        phase_name = SeasonQueryService.get_phase_name(season)

        can_edit = phase_name == SeasonPhase.SUBMISSION

        remaining_days = None
        if can_edit:
            remaining_days = SeasonQueryService.get_remaining_days(season)

        evaluation_ideas_count = None
        if phase_name == SeasonPhase.EVALUATION:
            evaluation_ideas_count = SeasonQueryService.get_evaluation_ideas_count(season)

        ideas = SeasonQueryService.get_season_ideas(season, ordering)

        return {
            "id": season.id,
            "name": season.name,
            "description": season.description,
            "start_date": season.start_date,
            "end_date": season.end_date,
            "ideas_count": SeasonQueryService.get_ideas_count(season),
            "phase": phase_name,
            "remaining_days": remaining_days,
            "evaluation_ideas_count": evaluation_ideas_count,

            "ideas": ideas
        }

    # =============================
    # 🔹 Form Design Page
    # =============================

    @staticmethod
    def get_form_design_data(season):
        phase_name = SeasonQueryService.get_phase_name(season)
        form = getattr(season, "form", None)

        data = {
            "season_info": {
                "season_name": season.name,
                "phase": phase_name,
                "ideas_count": SeasonQueryService.get_ideas_count(season),

                "show_remaining_days": False,
                "show_evaluation_count": False,
            },
            "form": {
                "title": form.title if form else "",
                "questions": SeasonQueryService.get_form_questions(season)
            }
        }

        #  SUBMISSION
        if phase_name == SeasonPhase.SUBMISSION:
            data["season_info"].update({
                "remaining_days": SeasonQueryService.get_remaining_days(season),
                "show_remaining_days": True
            })

        #  EVALUATION
        elif phase_name == SeasonPhase.EVALUATION:
            data["season_info"].update({
                "evaluation_ideas_count": SeasonQueryService.get_evaluation_ideas_count(season),
                "show_evaluation_count": True
            })

        return data
    
    @staticmethod
    def get_form_questions(season):
        form = getattr(season, "form", None)

        if not form:
            return []

        questions = form.questions.all().order_by("order").prefetch_related("choices")

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
                        "order": c.order,
                    }
                    for c in q.choices.all()
                ] if q.type in ["select", "select_multiple"] else []
            })

        return result
    @staticmethod
    def get_season_ideas(season, ordering=None):
        qs = season.ideas.select_related("owner").only(
            "id", "title", "created_at", "owner__full_name"
       )

        if ordering == "newest":
            qs = qs.order_by("-created_at")
        elif ordering == "oldest":
            qs = qs.order_by("created_at")
        elif ordering == "alphabet":
            qs = qs.order_by("title")
        else:
            qs = qs.order_by("-created_at")  # default

        return [
            {
                "id": idea.id,
                "project_name": idea.title,
                "submitted_by": idea.owner.full_name,
                "submitted_at": idea.created_at.strftime("%d/%m/%Y"),
            }
            for idea in qs
        ]
        
  
    @staticmethod
    def get_idea_details_with_form(idea):
        form = getattr(idea.season, "form", None)

        if not form:
            return {}

        questions = form.questions.all().order_by("order").prefetch_related("choices")

        formatted_answers = []
        answers = idea.answers or {}
        for q in questions:
            value = answers.get(q.key)
            if q.type in ["select", "select_multiple"] and value:
                choices_map = {c.value: c.label for c in q.choices.all()}

                if isinstance(value, list):
                    value = [choices_map.get(v, v) for v in value]
                else:
                    value = choices_map.get(value, value)

            formatted_answers.append({
                "question": q.label,
                "answer": value,
                "type": q.type
            })

        return formatted_answers

