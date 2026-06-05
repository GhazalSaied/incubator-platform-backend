from urllib import request
from datetime import datetime
from django.utils import timezone
from dateutil import parser
from rest_framework.exceptions import ValidationError
from django.db import transaction
from accounts.constants import SystemRoles
from accounts.role_service import RoleService
from core.events import EventBus
from ideas.models import Season, SuggestedVolunteer, TeamRequest
from ideas.phases import SeasonPhase
from volunteers.models import VolunteerProfile
from django.utils import timezone
from ideas.services.season_phase_service import SeasonPhaseService
from evaluations.models import EvaluationInvitation


class VolunteerManagementService:

    @staticmethod
    @transaction.atomic
    def approve_volunteer(*, volunteer_id):

        try:
            v = VolunteerProfile.objects.select_related("user").get(id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            raise ValidationError("المتطوع غير موجود")

        if v.status != VolunteerProfile.PENDING:
            raise ValidationError("لا يمكن قبول هذا الطلب")

        v.status = VolunteerProfile.APPROVED
        v.save(update_fields=["status"])
        RoleService.assign_role(
            user= v.user,
            role_code=SystemRoles.VOLUNTEER,
            assigned_by= None
        )
        EventBus.emit("volunteer_approved",user=v.user,actor=None)



        return v

    # ----------------------------------------

    @staticmethod
    @transaction.atomic
    def reject_volunteer(*, volunteer_id):

        try:
            v = VolunteerProfile.objects.select_related("user").get(id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            raise ValidationError("المتطوع غير موجود")

        if v.status != VolunteerProfile.PENDING:
            raise ValidationError("لا يمكن رفض هذا الطلب")

        v.status = VolunteerProfile.REJECTED
        v.save(update_fields=["status"])
        EventBus.emit(
    "volunteer_rejected",
    user=v.user,
    actor=None
)
        return v
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ازالة مقيم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    @staticmethod
    @transaction.atomic
    def remove_evaluator_role(*, volunteer_id, actor=None):

        try:
            volunteer = VolunteerProfile.objects.select_related("user").get(id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            raise ValidationError("المتطوع غير موجود")

        user = volunteer.user
        current_phase = SeasonPhaseService.get_current_phase()
        """"
        if current_phase in [
            SeasonPhase.EVALUATION,
            SeasonPhase.INCUBATION
        ]:
            raise ValidationError(
            "لا يمكن إزالة المقيم خلال مرحلة التقييم أو الاحتضان"
            )"""
        invitation = EvaluationInvitation.objects.filter(
            user=user,
            status="ACCEPTED"
        ).select_for_update().first()

        has_role = user.userrole_set.filter(
            role__code=SystemRoles.EVALUATOR,
            is_active=True
        ).exists()

        if not invitation and not has_role:
            raise ValidationError("هذا المستخدم ليس مقيم حالياً")

    #  revoke invitation
        if invitation:
            invitation.status = "REVOKED"
            invitation.responded_at = timezone.now()
            invitation.save(update_fields=["status", "responded_at"])

    #  remove role
        if has_role:
            RoleService.remove_role(
                user=user,
                role_code=SystemRoles.EVALUATOR
            )

        return {
            "success": True,
            "volunteer_id": volunteer.id
        }
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\إرسال دعوة تقييم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    @staticmethod
    @transaction.atomic
    def send_invitation_to_volunteer(
        *,
        volunteer_id,
        description,
        expected_duration,
        task,
        actor,
    ):
        season = SeasonPhaseService.get_current_season()

    #  تحقق الموسم
        try:
            season = Season.objects.get(id=season.id)
        except Season.DoesNotExist:
            raise ValidationError("الموسم غير موجود")

    #  جلب المتطوع أولاً
        try:
            v = VolunteerProfile.objects.select_related("user").get(user_id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            raise ValidationError("المتطوع غير موجود")
        
        v = VolunteerProfile.objects.select_related("user").get(user_id=volunteer_id)
    # تحقق أنه متطوع
        if SystemRoles.VOLUNTEER not in v.user.role_codes:
            raise ValidationError("هذا المستخدم ليس متطوعاً")
        if v.status != VolunteerProfile.APPROVED:
            raise ValidationError("لا يمكن إرسال دعوة لهذا المتطوع")

    #  منع التكرار
        exists = EvaluationInvitation.objects.filter(
            user=v.user,
            season=season,
            status__in=["PENDING", "ACCEPTED"]
        ).exists()

        if exists:
            raise ValidationError("هذا المتطوع لديه دعوة فعالة بالفعل")

    #  إنشاء الدعوة
        invitation = EvaluationInvitation.objects.create(
            user=v.user,
            season=season,
            description = description,
            expected_duration=expected_duration,
            task=task,
            created_by=actor
        )

        EventBus.emit(
            "evaluation_invitation_sent",
            invitation=invitation,
            actor=actor
        )

        return invitation
    
    

class TeamSuggestionService:

    @staticmethod
    @transaction.atomic
    def suggest_volunteers(*, team_request_id, volunteer_ids, actor):

        try:
            team_request = TeamRequest.objects.select_related("idea__owner").get(id=team_request_id)
        except TeamRequest.DoesNotExist:
            raise ValidationError("طلب الفريق غير موجود")

        #  لازم يكون PENDING
        if team_request.status != "PENDING":
            raise ValidationError("تم معالجة هذا الطلب مسبقاً")

        suggestions = []

        for vid in volunteer_ids:
            try:
                volunteer = VolunteerProfile.objects.get(id=vid)
            except VolunteerProfile.DoesNotExist:
                continue
            forbidden_roles = [SystemRoles.IDEA_OWNER,SystemRoles.INCUBATOR,]
            if any(role in volunteer.user.role_codes
                   for role in forbidden_roles):
                raise ValidationError( f"لا يمكن اقتراح المتطوع {volunteer.user.full_name} لأنه صاحب فكرة أو محتضن")

            suggestion = SuggestedVolunteer.objects.create(
                team_request=team_request,
                volunteer=volunteer
            )
            suggestions.append(suggestion)

        #  تغيير حالة الطلب
        team_request.status = "APPROVED"
        team_request.save(update_fields=["status"])

        #  إشعار لصاحب الفكرة
        EventBus.emit(
            "volunteers_suggested",
            idea=team_request.idea,
            volunteers=volunteer_ids,
            actor=actor
        )

        return {
            "team_request_id": team_request.id,
            "suggested_count": len(suggestions)
        }