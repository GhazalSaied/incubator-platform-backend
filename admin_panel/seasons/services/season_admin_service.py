from datetime import date, time
from django.db.models import Count
from core.events import EventBus
from ideas import phases
import ideas
from ideas.models import Season, Idea, IdeaStatus, IdeaForm, FormQuestion, FormQuestionChoice,SeasonStatus
from ideas.services.season_phase_service import SeasonPhaseService
from django.utils.timezone import datetime, now
from ideas.phases import SeasonPhase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from accounts.models import User
from django.db import transaction
from ideas.phases import SeasonPhase
from ideas.phases import SeasonPhase as PhaseEnum
from datetime import timedelta
from ideas.services.idea_transition_orchestrator import IdeaTransitionOrchestrator
from ideas.services.state.idea_state_service import IdeaStateService



class SeasonAdminService:

    @staticmethod
    @transaction.atomic
    def create_season(data):

        # validation
        if data["start_date"] >= data["end_date"]:
            raise ValidationError({
            "end_date": "تاريخ النهاية يجب أن يكون بعد البداية"
        })

        # 1. create season
        season = Season.objects.create(
            name=data["name"],
            description=data.get("description"),
            start_date=data["start_date"],
            end_date=data["end_date"]
        )

        

        return season
    



    @staticmethod
    @transaction.atomic
    def _create_phases(season):

        if SeasonPhase.objects.filter(season=season).exists():
            return

        start_datetime = timezone.make_aware(
            datetime.combine(
                season.start_date,
                time.min
            )
        )

        end_datetime = timezone.make_aware(
            datetime.combine(
                season.end_date,
                time.max
            )
        )

        SeasonPhase.objects.create(
            season=season,
            phase=SeasonPhase.SUBMISSION,
            start_date=start_datetime,
            end_date=end_datetime,
            order=1
        )
    
    
    @transaction.atomic 
    @staticmethod
    def publish_season(season):

        if not hasattr(season, "form"):
            raise ValidationError({
                "form": "لا يمكن نشر الموسم بدون نموذج"
            })

        if season.form.questions.count() == 0:
            raise ValidationError({
                "form": "النموذج فارغ"
            })

        if season.status != SeasonStatus.DRAFT:
            raise ValidationError({
                "status": "الموسم منشور مسبقاً"
            })

        current_phase = SeasonPhaseService.get_current_phase()

        if current_phase and current_phase.phase != SeasonPhase.EXHIBITION:
            raise ValidationError({
                "phase": "لا يمكن نشر موسم جديد قبل وصول الموسم الحالي إلى مرحلة المعرض"
            })
        
        season.is_open = True
        season.status = SeasonStatus.PUBLISHED
        season.save(update_fields=["is_open","status"])

        
        SeasonAdminService._create_phases(season)
        

        EventBus.emit("season_published",season=season)
        
    

        return season
    
    
   
    
    @staticmethod
    @transaction.atomic
    def close_submissions(season):
        if season.status != SeasonStatus.PUBLISHED:
            raise ValidationError({
                "status": "الموسم غير منشور"
            })
        if not season.is_open:
            raise ValidationError({
                "is_open": "الموسم مغلق بالفعل"
            })
        if season.ideas.filter(status=IdeaStatus.SUBMITTED).count() == 0:
            raise ValidationError({
                "ideas": "لا يمكن إغلاق الموسم بدون أفكار مقدمة"
            })
        phase = SeasonPhaseService.get_current_phase(season)

        if not phase:
            raise ValidationError({
                "phase": "لا توجد مرحلة حالية"
            })

        if phase.phase != SeasonPhase.SUBMISSION:
            raise ValidationError({
                "phase": "المرحلة الحالية ليست مرحلة التقديم"
            })
        season.is_open = False
        season.status = SeasonStatus.CLOSED
        season.save(update_fields=["is_open", "status"])
        ideas = Idea.objects.filter(season=season,status=IdeaStatus.SUBMITTED)
        
        
        if ideas.exists():
            IdeaTransitionOrchestrator.change_status(idea=ideas.first(),to_status=IdeaStatus.PRE_ACCEPTED,user=None)
        ideas = Idea.objects.filter(season=season,status=IdeaStatus.SUBMITTED)
        for idea in ideas:
            IdeaStateService.change_status(idea=idea,to_status=IdeaStatus.PRE_ACCEPTED,user=None)
        

        EventBus.emit("bootcamp_started",season=season)
        return season

