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

#//////////////////////// GET USER IDEA //////////////////

    @staticmethod
    def get_user_idea(user):
        from ideas.models import Idea

        try:
            return Idea.objects.get(owner=user)
        except Idea.DoesNotExist:
            raise ValueError("لا يوجد فكرة")

#///////////////////// INCUBATION DATA ////////////////////

    @staticmethod
    def get_incubation_data(user):

        idea = IdeaService.get_user_idea(user)

        if idea.status != IdeaStatus.INCUBATED:
            raise ValueError("لم يتم الاحتضان بعد")

        reviews = idea.reviews.order_by("-meeting_date")

        from evaluations.serializers import IncubationReviewSerializer

        return {
            "phase": "INCUBATION",
            "warning": "عدم تحقيق تقدم قد يؤدي لإنهاء الاحتضان",
            "next_review": IncubationReviewSerializer(reviews.first()).data if reviews else None,
            "reviews": IncubationReviewSerializer(reviews, many=True).data,
            "can_request_consultation": True
        }


#///////////////////// EXHIBITION  DATA ////////////////////

    @staticmethod
    def get_exhibition_data(user):

        idea = IdeaService.get_user_idea(user)

        return {
            "phase": "EXHIBITION",
            "message": "يرجى تجهيز بطاقة المشروع للمعرض",
            "exhibition_date": idea.exhibition_date,
            "data": {
                "title": idea.title,
                "image": idea.exhibition_image,
                "project_goal": idea.project_goal,
                "project_services": idea.project_services,
                "owner_email": idea.owner.email,
                "team": [
                    {
                        "email": m.user.email,
                        "role": m.role
                    }
                    for m in idea.team_members.all()
                ]
            }
        }

#///////////////////// UPDATE EXHIBITION ////////////////////

@staticmethod
def update_exhibition(user, data, files):

    idea = IdeaService.get_user_idea(user)

    from ideas.serializers import ExhibitionSerializer

    serializer = ExhibitionSerializer(
        idea,
        data=data,
        partial=True
    )
    serializer.is_valid(raise_exception=True)

    idea = serializer.save()

    # image handling
    if "exhibition_image" in files:
        idea.exhibition_image = files["exhibition_image"]
        idea.save()

    return idea

#////////////////////// CREATE TEAM REQUEST /////////////////////

    @staticmethod
    def create_team_request(user, data):

        idea = IdeaService.get_user_idea(user)

        from ideas.serializers import TeamRequestSerializer

        serializer = TeamRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return serializer.save(idea=idea)
    

#////////////////////////// SUGGESTED VOLUNTEERS ////////////////////////

@staticmethod
def get_suggested_volunteers():

    from volunteers.models import VolunteerProfile

    volunteers = VolunteerProfile.objects.filter(status="APPROVED")

    return [
        {
            "name": v.user.full_name,
            "email": v.user.email,
            "role": v.volunteer_type
        }
        for v in volunteers
    ]

#//////////////////////// GET CONSULTANTS //////////////////

@staticmethod
def get_consultants():

    from volunteers.models import VolunteerProfile

    volunteers = VolunteerProfile.objects.filter(status="APPROVED")

    return [
        {
            "name": getattr(v.user, "full_name", v.user.email),
            "email": v.user.email,
            "specialization": v.volunteer_type,
            "availability": v.availability_type
        }
        for v in volunteers
    ]