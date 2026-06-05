from django.db import transaction
from django.shortcuts import get_object_or_404
from ideas.models import ( Idea,FormQuestion,
                           IdeaStatus, Season ,
                            IdeaAuditLog , TeamRequest ,
                            TeamStatus,TeamMember
                        )
from accounts.role_service import RoleService
from accounts.constants import SystemRoles
from ideas.services.idea_validation import IdeaValidationService
from core.events import EventBus
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase
from ideas.serializers import TeamRequestSerializer
from notifications.services.notification_service import NotificationService
from ideas.services.idea_workflow import IdeaWorkflow
from ideas.services.state.idea_state_service import IdeaStateService
from evaluations.serializers import IncubationReviewSerializer
from volunteers.models import VolunteerProfile
from core.exceptions import BusinessLogicException
from rest_framework.exceptions import ValidationError
from ideas.phases import (
    get_current_phase,
    SeasonPhase,
)


from django.contrib.auth import get_user_model
User = get_user_model()

class IdeaService:


    
 
 #///////////////////////////////// GET SUBMISSION FORM ///////////////////////////

    @classmethod
    def get_submission_form(cls, user, season):

        cls._validate_submission_access(season)

        form = season.form

        draft = Idea.objects.filter(
            owner=user,
            season=season,
        ).first()

        steps = form.steps.prefetch_related(
            "questions__choices"
        ).all()

        completed_steps = []

        for step in steps:
            if cls._is_step_completed(step, draft):
                completed_steps.append(step.order)

        return {
            "form_id": form.id,
            "form_title": form.title,
            "current_step": cls._resolve_current_step(
                steps,
                completed_steps
            ),
            "total_steps": steps.count(),
            "completed_steps": completed_steps,
            "idea_status": draft.status if draft else None,
            "draft_data": cls._build_draft_payload(draft),
            "steps": [
                cls._serialize_step(step)
                for step in steps
            ]
        }


#///////////////////////////// GET OR CREATE DRAFT //////////////////////////

    @classmethod
    def _get_or_create_draft(cls, user, season):

        submitted_exists = Idea.objects.filter(
            owner=user,
            season=season,
            status=IdeaStatus.SUBMITTED
        ).exists()

        if submitted_exists:
            raise ValidationError(
                "لا يمكنك إنشاء فكرة جديدة بعد إرسال فكرة بهذا الموسم"
            )

        draft = Idea.objects.filter(
            owner=user,
            season=season,
            status=IdeaStatus.DRAFT
        ).first()

        if draft:
            return draft

        return Idea.objects.create(
            owner=user,
            season=season,
            status=IdeaStatus.DRAFT,

            # static placeholders
            title="Draft",
            description="",
            target_audience="",
            sector="",

            answers={}
        )


#///////////////////////////////// SAVE STEP //////////////////////////////

    @classmethod
    @transaction.atomic
    def save_step(cls, user, season, step_order, payload):

        cls._validate_submission_access(season)

        idea = cls._get_or_create_draft(user, season)

        if not idea.can_be_edited():
            raise ValidationError("لا يمكن تعديل الفكرة بعد الإرسال")

        form = season.form

        step = get_object_or_404(
            form.steps.prefetch_related("questions__choices"),
            order=step_order
        )

        validated_data = IdeaValidationService.validate_step(
            step,
            payload
        )

        cls._apply_validated_data(
            idea,
            step,
            validated_data
        )

        idea.save()

        return idea



#/////////////////////////////// SUBMIT IDEA ////////////////////////////////

    @classmethod
    @transaction.atomic
    def submit_idea(cls, user, season):

        cls._validate_submission_access(season)

        idea = Idea.objects.select_for_update().filter(
            owner=user,
            season=season,
        ).first()

        if not idea:
            raise ValidationError("لا يوجد draft للإرسال")

        if idea.status == IdeaStatus.SUBMITTED:
            raise ValidationError("تم إرسال الفكرة مسبقاً")

        IdeaValidationService.validate_full_submission(
            season.form,
            idea
        )

        idea.status = IdeaStatus.SUBMITTED
        idea.save(update_fields=["status", "updated_at"])

        RoleService.assign_role(
            user=user,
            role_code=SystemRoles.IDEA_OWNER,
        )

        EventBus.emit(
            'idea_submitted',
            idea=idea,
            actor=user,
        )

        return idea


#/////////////////////////////// VALIDATE SUBMISSION ACCESS ////////////////////////
    @classmethod
    def _validate_submission_access(cls, season):

        if season.status != "PUBLISHED":
            raise ValidationError("الموسم غير منشور")

        current_phase = get_current_phase(season)

        if not current_phase:
            raise ValidationError("لا يوجد phase نشطة")

        if current_phase.phase != SeasonPhase.SUBMISSION:
            raise ValidationError("مرحلة التقديم غير متاحة")



#//////////////////////////// APPLY VALIDATED DATA ///////////////////////////////


    @classmethod
    def _apply_validated_data(cls, idea, step, validated_data):

        answers = dict(idea.answers)

        for question in step.questions.all():

            if question.key not in validated_data:
                continue

            value = validated_data[question.key]

            if question.source == FormQuestion.STATIC:
                setattr(
                    idea,
                    question.static_field,
                    value
                )

            else:
                answers[question.key] = value

        idea.answers = answers


#/////////////////////////////// SERIALIZER STEP ////////////////////

    @classmethod
    def _serialize_step(cls, step):

        return {
            "id": step.id,
            "title": step.title,
            "order": step.order,
            "questions": [
                {
                    "id": q.id,
                    "key": q.key,
                    "label": q.label,
                    "type": q.type,
                    "required": q.required,
                    "order": q.order,
                    "source": q.source,
                    "static_field": q.static_field,
                    "placeholder": q.placeholder,
                    "help_text": q.help_text,
                    "choices": [
                        {
                            "id": c.id,
                            "value": c.value,
                            "label": c.label,
                            "order": c.order,
                        }
                        for c in q.choices.all()
                    ]
                }
                for q in step.questions.all().order_by("order")
            ]
        }
    

#////////////////////////////////////// BUILD DRAFT /////////////////////////

    @classmethod
    def _build_draft_payload(cls, idea):

        if not idea:
            return {}

        return {
            "title": idea.title,
            "description": idea.description,
            "target_audience": idea.target_audience,
            "sector": idea.sector,
            **idea.answers
        }
    

#////////////////////////////////////// CURRENT STEP //////////////////////
    
    @classmethod
    def _resolve_current_step(cls, steps, completed_steps):

        for step in steps:
            if step.order not in completed_steps:
                return step.order

        return steps.last().order if steps.exists() else 1


#///////////////////////////// CHECK COMPLETED STEPS /////////////////////

    @classmethod
    def _is_step_completed(cls, step, idea):

        if not idea:
            return False

        for question in step.questions.all():

            value = None

            if question.source == FormQuestion.STATIC:
                value = getattr(idea, question.static_field)
            else:
                value = idea.answers.get(question.key)

            if question.required and value in [None, "", []]:
                return False

        return True




#//////////////////////// GET USER IDEA //////////////////

    @staticmethod
    def get_user_idea(user):
        idea = Idea.objects.filter(owner=user).order_by("-created_at").first()

        if not idea:
            raise ValueError("لا يوجد فكرة")

        return idea

#/////////////////////////// GET USER IDEA (BOTH OWNER AND TEAM MEMBER) //////////////////////////    

    @staticmethod
    def get_dashboard_idea(user):

        owner_idea = (
            Idea.objects
            .filter(owner=user)
            .select_related("season")
            .order_by("-created_at")
            .first()
        )

        if owner_idea:
            return owner_idea

        member = (
            TeamMember.objects
            .select_related(
                "idea",
                "idea__season",
            )
            .filter(user=user)
            .order_by("-joined_at")
            .first()
        )

        if member:
            return member.idea

        raise ValueError("لا يوجد فكرة")

#///////////////////// INCUBATION DATA ////////////////////
#UNUSED
    @staticmethod
    def get_incubation_data(user):

        idea = IdeaService.get_user_idea(user)

        if idea.status != IdeaStatus.INCUBATION:
            raise ValueError("لم يتم الاحتضان بعد")

        reviews = idea.reviews.order_by("-meeting_date")

        return {
            "phase": "INCUBATION",
            "warning": "عدم تحقيق تقدم قد يؤدي لإنهاء الاحتضان",
            "next_review": IncubationReviewSerializer(reviews.first()).data if reviews else None,
            "reviews": IncubationReviewSerializer(reviews, many=True).data,
            "can_request_consultation": True
        }



    #////////////////////// CREATE TEAM REQUEST /////////////////////

    @staticmethod
    def create_team_request(user, data):

        try:
            idea = IdeaService.get_user_idea(user)
        except ValueError:
            return {
                "has_team": False,
                "current_team": []
            }

        #  أولاً تحقق قبل الإنشاء
        if TeamRequest.objects.filter(
            idea=idea,
            status="PENDING"
        ).exists():
            raise ValueError("لديك طلب فريق قيد المراجعة")

        serializer = TeamRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        team_request = serializer.save(idea=idea)


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
            team_request= team_request,
            idea= idea.id,
            actor=user,
        )

            

        return team_request


    #////////////////////////// SUGGESTED VOLUNTEERS ////////////////////////

    @staticmethod
    def get_suggested_volunteers(user):

        from ideas.models import TeamRequest, SuggestedVolunteer

        idea = IdeaService.get_user_idea(user)

        team_request = (
            TeamRequest.objects.filter(
                idea=idea,
                status="APPROVED"
            )
            .order_by("-created_at")
            .first()
        )

        if not team_request:
            return []

        suggested = (
            SuggestedVolunteer.objects.filter(
                team_request=team_request
            )
            .select_related("volunteer__user")
        )

        return [
            {
                "id": s.volunteer.user.id,
                "name": s.volunteer.user.full_name,
                "email": s.volunteer.user.email,
                "primary_skill": s.volunteer.primary_skills,
            }
            for s in suggested
        ]
    

    #/////////////////// PROJECT DETAILS (VOLUNTEER & INCUBATOR ) //////////////////

    @staticmethod
    def get_project_details(user):

        idea = (
            IdeaService.get_dashboard_idea(user)
        )

        team_members = []

        # owner first
        team_members.append({
            "name": idea.owner.full_name
        })

        members = (
            idea.team_members
            .select_related("user")
            .all()
        )

        for member in members:
            team_members.append({
                "name": member.user.full_name
            })

        return {
            "idea": idea,
            "team_members": team_members
        }

    #//////////////////////// GET CONSULTANTS //////////////////
    #UNUSED
    @staticmethod
    def get_consultants():

        

        volunteers = VolunteerProfile.objects.filter(status="APPROVED")

        return [
            {
                "id": v.id,
                "name": getattr(v.user, "full_name", v.user.email),
                "email": v.user.email,
                "category": v.volunteer_type,
                "availability": v.availability_type,
                "primary_skill": v.primary_skills,
                "availability": v.availability,
            }
            for v in volunteers
        ]


    #///////////////////////// TEAM DASHBOARD ///////////////////////
    #UNUSED
    @staticmethod
    def get_team_dashboard(user):

        idea = IdeaService.get_user_idea(user)
        
        if not idea:
            return {
                "team_status": "no_idea",
                "current_team": [],
                "suggested_volunteers": [],
                "user_context": {
                    "is_idea_owner": False,
                    "is_volunteer": hasattr(user, "volunteer_profile")
                }
            }

        # team
        team = idea.team_members.select_related("user")

        current_team = [
            {
                "id": m.user.id,
                "name": getattr(m.user, "full_name", m.user.email),
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
    
#////////////////////////// UPDATE IDAE //////////////////////
#UNUSED
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
#UNUSED
    @staticmethod
    def withdraw_idea(*, user, idea):

        # 1 التحقق من المرحلة
        if not SeasonPhaseService.is_phase(SeasonPhase.SUBMISSION):
            raise PermissionError("لا يمكن سحب الفكرة خارج مرحلة التقديم")

        # 2 التحقق من الحالة
        if idea.status not in [IdeaStatus.DRAFT, IdeaStatus.SUBMITTED]:
            raise ValueError("لا يمكن سحب هذه الفكرة في حالتها الحالية")

        # 3 تنفيذ السحب
        IdeaStateService.change_status(
            idea=idea,
            to_status=IdeaStatus.WITHDRAWN,
            user=user,
            reason="user_withdraw"
        )

        EventBus.emit(
            "idea_withdrawn",
            payload={
                "idea": idea.id,
            },
            actor=user,
        )
        return idea