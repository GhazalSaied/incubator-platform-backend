from django.db import transaction
from ideas.models import Idea, IdeaStatus, Season
from ideas.services.idea_validation import IdeaFormValidator
from core.events import EventBus
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase


class IdeaService:

#/////////////////////// SUBMIT IDAE //////////////////////

    @staticmethod
    @transaction.atomic
    def submit_idea(*, user, data: dict):
        """
        مسؤول عن:
        - التحقق من الموسم
        - التحقق من الفورم الديناميكي
        - إنشاء الفكرة
        - إطلاق event
        """

        # 1 جلب الموسم المفتوح
        season = Season.objects.filter(is_open=True).first()

        if not season or not hasattr(season, "form"):
            raise ValueError("التقديم مغلق حالياً")

        answers = data.get("answers", {})

        # 2 Dynamic Form Validation
        validator = IdeaFormValidator(season.form, answers)
        validator.validate()

        # 3 إنشاء الفكرة
        idea = Idea.objects.create(
            owner=user,
            season=season,
            title=data.get("title"),
            description=data.get("description"),
            answers=answers,
            status=IdeaStatus.SUBMITTED
        )

        # 4 إطلاق event 
        EventBus.publish(
            "idea_status_changed",
            idea=idea,
            new_status=IdeaStatus.SUBMITTED
        )

        return idea
    
#////////////////////////// UPDATE IDAE //////////////////////

    @staticmethod
    def update_idea(*, user, idea, data: dict):

        # 1 التحقق من المرحلة
        if not SeasonPhaseService.is_phase(SeasonPhase.SUBMISSION):
            raise PermissionError("لا يمكن تعديل الفكرة خارج مرحلة التقديم")

        # 2 التحقق من الحالة
        if not idea.can_be_edited():
            raise PermissionError("لا يمكن تعديل الفكرة في حالتها الحالية")

        # 3 التعديل
        for field in ["title", "description", "answers"]:
            if field in data:
                setattr(idea, field, data[field])

        idea.save()

        return idea

#///////////////////////////////// WITHDRAW IDEA /////////////////////////

    @staticmethod
    def withdraw_idea(*, user, idea):

        # 1 التحقق من المرحلة
        if not SeasonPhaseService.is_phase(SeasonPhase.SUBMISSION):
            raise PermissionError("لا يمكن سحب الفكرة خارج مرحلة التقديم")

        # 2 التحقق من الحالة
        if idea.status not in ["DRAFT", "SUBMITTED"]:
            raise ValueError("لا يمكن سحب هذه الفكرة في حالتها الحالية")

        # 3 تنفيذ السحب
        idea.status = "WITHDRAWN"
        idea.save()

        #  event
        EventBus.publish(
            "idea_status_changed",
            idea=idea,
            new_status="WITHDRAWN"
        )

        return idea