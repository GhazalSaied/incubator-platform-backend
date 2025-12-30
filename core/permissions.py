from rest_framework.permissions import BasePermission
from accounts.models import UserRole
from django.utils import timezone
from django.db import models



#///////////////// HAS ROLE ///////////////////////////////

class HasRole(BasePermission):
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
    
#/////////////////// PERMISSIONS ///////////////////////////

class IsIdeaOwner(HasRole):
    required_role_code = "IDEA_OWNER"


class IsVolunteer(HasRole):
    required_role_code = "VOLUNTEER"


class IsEvaluator(HasRole):
    required_role_code = "EVALUATOR"


class IsAdmin(HasRole):
    required_role_code = "ADMIN"
