from ideas.models import Season, Idea, IdeaStatus
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date
from django.db.models import Count
from ideas.models import Idea,Season,IdeaForm,FormQuestion,FormQuestionChoice
from ideas.services.season_phase_service import SeasonPhaseService
from django.utils.timezone import now
from ideas.phases import SeasonPhase
from django.utils import timezone
from django.core.exceptions import ValidationError
from notifications.models import Notification
from django.contrib.auth import get_user_model
from accounts.models import User
class SeasonPhaseTypes:
    SUBMISSION = "SUBMISSION"
    BOOTCAMP = "BOOTCAMP"
    EVALUATION = "EVALUATION"
    INCUBATION = "INCUBATION"
    EXHIBITION = "EXHIBITION"


class SeasonAdminService:

    # =============================
    # 🔹 Shared Helpers
    # =============================

    @staticmethod
    def get_current_phase_name(season):
        current_phase = SeasonPhaseService.get_current_phase(season)
        return current_phase.phase if current_phase else None

    @staticmethod
    def get_ideas_count(season):
        return season.ideas.count()

    @staticmethod
    def get_evaluation_ideas_count(season):
        return season.ideas.filter(
            status="UNDER_EVALUATION"
        ).count()

    @staticmethod
    def get_remaining_days(season):
        return (season.end_date - date.today()).days

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
        phase_name = SeasonAdminService.get_current_phase_name(season)

        return {
            "id": season.id,
            "name": season.name,
            "start_date": season.start_date,
            "end_date": season.end_date,
            "ideas_count": season.ideas_count,
            "status": SeasonAdminService.get_season_status(
                season,
                phase_name
            )
        }

    @staticmethod
    def list_seasons(year=None):
        qs = Season.objects.all()

        if year:
            qs = qs.filter(start_date__year=year)

        qs = qs.annotate(
            ideas_count=Count("ideas")
        )

        return [
            SeasonAdminService.build_season_response(season)
            for season in qs
        ]

    # =============================
    # 🔹 Season Details Page
    # =============================

    @staticmethod
    def get_season_details(season):
        phase_name = SeasonAdminService.get_current_phase_name(season)

        can_edit = phase_name == SeasonPhaseTypes.SUBMISSION

        remaining_days = None
        if can_edit:
            remaining_days = SeasonAdminService.get_remaining_days(season)

        evaluation_ideas_count = None
        if phase_name == SeasonPhaseTypes.EVALUATION:
            evaluation_ideas_count = SeasonAdminService.get_evaluation_ideas_count(season)

        return {
            "id": season.id,
            "name": season.name,
            "description": season.description,
            "start_date": season.start_date,
            "end_date": season.end_date,
            "ideas_count": SeasonAdminService.get_ideas_count(season),
            "phase": phase_name,
            "can_edit": can_edit,
            "remaining_days": remaining_days,
            "evaluation_ideas_count": evaluation_ideas_count
        }

    # =============================
    # 🔹 Form Design Page
    # =============================

    @staticmethod
    def get_form_design_data(season):
        phase_name = SeasonAdminService.get_current_phase_name(season)

        data = {
            "season_info": {
                "season_name": season.name,
                "phase": phase_name,
                "ideas_count": SeasonAdminService.get_ideas_count(season),

                "show_remaining_days": False,
                "show_evaluation_count": False,
            },
            "form": {
                "title": season.form.title if hasattr(season, "form") else "",
                "questions": SeasonAdminService.get_form_questions(season)
            }
        }

        # 🟢 SUBMISSION
        if phase_name == SeasonPhaseTypes.SUBMISSION:
            data["season_info"].update({
                "remaining_days": SeasonAdminService.get_remaining_days(season),
                "show_remaining_days": True
            })

        # 🔵 EVALUATION
        elif phase_name == SeasonPhaseTypes.EVALUATION:
            data["season_info"].update({
                "evaluation_ideas_count": SeasonAdminService.get_evaluation_ideas_count(season),
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
        qs = season.ideas.select_related("owner")

    # 🧠 sorting
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
                "submitted_at": idea.created_at,
            }
            for idea in qs
        ]
        
    @staticmethod
    def get_review_submissions_data(season, ordering=None):
    # 🔥 reuse
        base_data = SeasonAdminService.get_form_design_data(season)

        ideas = SeasonAdminService.get_season_ideas(season, ordering)

        return {
            "season_info": base_data["season_info"],
            "ideas": ideas
        }
    @staticmethod
    def get_idea_details_with_form(idea):
        form = getattr(idea.season, "form", None)

        if not form:
            return {}

        questions = form.questions.all().order_by("order").prefetch_related("choices")

        formatted_answers = []

        for q in questions:
            value = idea.answers.get(q.key)

        # 🔥 تحويل select ل label
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



    @staticmethod
    def create_season(data):

        # ✅ validation هون
        if data["start_date"] >= data["end_date"]:
            raise Exception("تاريخ النهاية يجب أن يكون بعد البداية")

        return Season.objects.create(
            name=data["name"],
            description=data.get("description"),
            start_date=data["start_date"],
            end_date=data["end_date"]
        )
    
    @staticmethod
    def publish_season(season):

        # 1️⃣ لازم يكون في فورم
        if not hasattr(season, "form"):
            raise Exception("لا يمكن نشر الموسم بدون نموذج")

        # 2️⃣ الفورم لازم فيه أسئلة
        if season.form.questions.count() == 0:
            raise Exception("النموذج فارغ")

        # 3️⃣ ما يكون منشور قبل
        if season.phases.exists():
            raise Exception("الموسم منشور مسبقاً")

        # 4️⃣ ما يكون في موسم تاني مفتوح
        active_submission_exists = SeasonPhase.objects.filter(
            phase ="submission",
            start_date__lte=now(),
            end_date__gte=now()
        ).exists()

        if active_submission_exists:
            raise Exception("في موسم مفتوح حالياً")

        # 5️⃣ إنشاء مرحلة التقديم
        SeasonPhase.objects.create(
            season=season,
            phase ="submission",
            start_date=season.start_date,
            end_date=season.end_date,
            order=1  
        )

        
        SeasonAdminService._notify_users_season_opened(season)

        return season
    
    
    User = get_user_model()
        
    @staticmethod
    def _notify_users_season_opened(season):

        users = User.objects.all()

        notifications = [
            Notification(
                user=user,
                title="فتح موسم جديد",
                message=f"تم فتح موسم {season.name} للتقديم قم بزيارة المنصة لتقديم أفكارك"
            )
            for user in users
        ]

        Notification.objects.bulk_create(notifications)


    @staticmethod
    def close_submissions(season):

        # ✅ تحقق: لازم يكون بمرحلة التقديم
        if not season.is_open:
            raise ValidationError("الموسم مغلق بالفعل")


        
        
        now = timezone.now()
        current_phase = season.phases.filter(end_date__isnull=True).first()
        if current_phase:
            current_phase.end_date = now
            current_phase.save()
            
        # 🟥 إغلاق التقديم
        season.is_open = False
        season.save()

        # 🟪 إرسال إشعارات
        SeasonAdminService._notify_users_season_closed(season)
        

    User = get_user_model()


    @staticmethod
    def _notify_users_season_closed(season):

        users = User.objects.all()

        notifications = [
            Notification(
                user=user,
                title="إغلاق التقديم",
                message=f"تم إغلاق التقديم لموسم {season.name}"
            )
            for user in users
        ]

        Notification.objects.bulk_create(notifications)