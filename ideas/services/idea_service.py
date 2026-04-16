from django.db import transaction
from ideas.models import Idea, IdeaStatus, Season , IdeaAuditLog , TeamRequest
from ideas.services.idea_validation import IdeaFormValidator
from core.events import EventBus
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase
from ideas.serializers import TeamRequestSerializer
from notifications.services.notification_service import NotificationService


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

        # جلب الموسم المفتوح
        season = Season.objects.filter(is_open=True).first()

        if not season or not hasattr(season, "form"):
            raise ValueError("التقديم مغلق حالياً")

        answers = data.get("answers", {})

        #  Dynamic Form Validation
        validator = IdeaFormValidator(season.form, answers)
        validator.validate()

        #  إنشاء الفكرة
        idea = Idea.objects.create(
            owner=user,
            season=season,
            title=data.get("title"),
            description=data.get("description"),
            answers=answers,
            status=IdeaStatus.SUBMITTED
        )

        EventBus.emit(
            "idea_submitted",
            payload={
                "idea": idea,
            },
            actor=user,
            action_url=f"/ideas/{idea.id}"
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
        if idea.status not in [IdeaStatus.DRAFT, IdeaStatus.SUBMITTED]:
            raise ValueError("لا يمكن سحب هذه الفكرة في حالتها الحالية")

        # 3 تنفيذ السحب
        idea.status = IdeaStatus.WITHDRAWN
        idea.save()
        EventBus.emit(
            "idea_withdrawn",
            payload={
                "idea": idea,
            },
            actor=user,
            action_url="/my-ideas"
        )
        return idea

#//////////////////////// GET USER IDEA //////////////////

    @staticmethod
    def get_user_idea(user):
        from ideas.models import Idea

        try:
            return Idea.objects.filter(owner=user).order_by("-created_at").first()
        except Idea.DoesNotExist:
            raise ValueError("لا يوجد فكرة")

#///////////////////// INCUBATION DATA ////////////////////

    @staticmethod
    def get_incubation_data(user):

        idea = IdeaService.get_user_idea(user)

        if idea.status != IdeaStatus.INCUBATION:
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
                        "name": m.user.full_name,
                        "email": m.user.email,
                        "role": m.role,
                        "is_owner": m.user == idea.owner
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

    #  أولاً تحقق قبل الإنشاء
    if TeamRequest.objects.filter(
        idea=idea,
        status="PENDING"
    ).exists():
        raise ValueError("لديك طلب فريق قيد المراجعة")

    serializer = TeamRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    team_request = serializer.save(idea=idea)

    # تحديث حالة الفريق
    idea.team_status = "team_building"
    idea.save()

    # Audit log
    IdeaAuditLog.objects.create(
        idea=idea,
        from_status="NO_TEAM",
        to_status="TEAM_REQUESTED",
        performed_by=user
    )

    # Notification
    EventBus.emit(
        "team_request_created",
        payload={
            "team_request": team_request,
            "idea": idea,
        },
        actor=user,
        action_url=f"/team-requests/{team_request.id}"
    )
        

    return team_request


#////////////////////////// SUGGESTED VOLUNTEERS ////////////////////////

@staticmethod
def get_suggested_volunteers(user):

    from ideas.models import TeamRequest, SuggestedVolunteer

    idea = IdeaService.get_user_idea(user)

    team_request = TeamRequest.objects.filter(
        idea=idea,
        status="APPROVED"
    ).last()

    if not team_request:
        return []

    suggested = SuggestedVolunteer.objects.filter(
        team_request=team_request
    ).select_related("volunteer__user")

    return [
        {
            "id": s.volunteer.id,
            "name": s.volunteer.user.full_name,
            "email": s.volunteer.user.email,
            "role": s.volunteer.primary_skills
        }
        for s in suggested
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


#///////////////////////// TEAM DASHBOARD ///////////////////////

@staticmethod
def get_team_dashboard(user):

    idea = IdeaService.get_user_idea(user)

    # team
    team = idea.team_members.select_related("user")

    current_team = [
        {
            "id": m.user.id,
            "name": m.user.full_name,
            "email": m.user.email,
            "role": m.role
        }
        for m in team
    ]

    # suggested
    suggested = IdeaService.get_suggested_volunteers(user)

    return {
        "team_status": getattr(idea, "team_status", "team_building"),
        "current_team": current_team,
        "suggested_volunteers": suggested,
        "user_context": {
            "is_idea_owner": True,
            "is_volunteer": hasattr(user, "volunteer_profile")
        }
    }