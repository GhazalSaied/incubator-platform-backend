from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
from django.db import models
from ideas.phases import SeasonPhase
from ideas.services.season_phase_service import SeasonPhaseService
from accounts.models import UserRole

#//////////////////////// PUBLIC PERMISSION (REUSABLE) ///////////////////////////////

class IsInPhase(BasePermission):
    """
    يسمح بالوصول فقط إذا كانت المنصة في مرحلة محددة
    """

    required_phase = None

    def has_permission(self, request, view):
        if not self.required_phase:
            return False

        return SeasonPhaseService.is_phase(self.required_phase)

# ──────────────── الأدوار القديمة  ────────────────
class HasRole(BasePermission):
    """
    فحص إذا كان لليوزر دور معين (role.code) ونشط ولم ينتهي صلاحيته
    """
    required_role_code = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not self.required_role_code:
            return False

        return UserRole.objects.filter(
            user=request.user,
            role__code=self.required_role_code,
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) |
            models.Q(expires_at__gt=timezone.now())
        ).exists()


class IsIdeaOwner(HasRole):
    required_role_code = "IDEA_OWNER"



#//////////////////// VOLUNTEER ///////////////////////////

class IsVolunteer(HasRole):
    required_role_code = "VOLUNTEER"

    def has_permission(self, request, view):
        base_permission = super().has_permission(request, view)

        if not base_permission:
            return False

        if not hasattr(request.user, "volunteer_profile"):
            return False

        return (
            request.user.volunteer_profile.status ==
            request.user.volunteer_profile.APPROVED
        )


class IsEvaluator(HasRole):
    required_role_code = "EVALUATOR"


class IsAdmin(HasRole):
    required_role_code = "ADMIN"



#/////////////////// SUBMIT IDEA ///////////////////////

class CanSubmitIdea(IsIdeaOwner, IsInPhase):
    
    required_phase = SeasonPhase.SUBMISSION


#////////////////// EDIT IDEA ////////////////////////////

class CanEditIdea(IsIdeaOwner, IsInPhase):
    
    required_phase = SeasonPhase.SUBMISSION

#//////////////////// EVALUATE IDEA /////////////////////

class CanEvaluateIdea(IsEvaluator, IsInPhase):

    required_phase = SeasonPhase.EVALUATION

# ──────────────── الغروبات الجديدة (Groups) اللي رتبتيها بالإنجليزي ────────────────
class IsDirector(BasePermission):
    """
    اليوزر لازم يكون في غروب 'Incubator Director'
    """
    message = "يجب أن تكون مديرة الحاضنة للوصول إلى هذه الوظيفة."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_active and
            request.user.groups.filter(name="incubator directors").exists()
        )


class IsSecretary(BasePermission):
    """
    اليوزر لازم يكون في غروب 'Incubator Secretary'
    """
    message = "يجب أن تكون سكرتيرة الحاضنة للوصول إلى هذه الوظيفة."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_active and
            request.user.groups.filter(name="incubator secretary").exists()
        )


class IsAdminOrSecretary(BasePermission):
    """
    اليوزر لازم يكون مديرة أو سكرتيرة
    """
    message = "يجب أن تكون مديرة أو سكرتيرة الحاضنة."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_active and
            (
                request.user.groups.filter(name="incubator directors").exists() or
                request.user.groups.filter(name="incubator secretary").exists()
            )
        )


class IsReadOnly(BasePermission):
    """
    الوصول للقراءة فقط (GET, HEAD, OPTIONS)
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

