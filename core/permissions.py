from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
from django.db import models
from accounts.models import UserRole


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


class IsVolunteer(HasRole):
    required_role_code = "VOLUNTEER"


class IsEvaluator(HasRole):
    required_role_code = "EVALUATOR"


class IsAdmin(HasRole):
    required_role_code = "ADMIN"


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