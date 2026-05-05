from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
from django.db import models
from ideas.phases import SeasonPhase
from ideas.services.season_phase_service import SeasonPhaseService
from accounts.models import UserRole
from accounts.models import Permission
from rest_framework.permissions import BasePermission


PERMISSIONS = {
    "idea.submit": "Submit Idea",
    "idea.view": "View Idea",

    "evaluation.submit": "Submit Evaluation",

    "user.manage": "Manage Users",
    "season.manage": "Manage Season",
    "bootcamp.manage": "Manage Bootcamp",
    "candecidebootcamp.manage": "Manage Candidate Bootcamp",
    "evaluation.manage": "Manage Evaluations",
    "evaluation_decision.manage": "Manage Evaluation Decisions",
}
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
PHASE_GATED_PERMISSIONS = {
    "idea.submit": SeasonPhase.SUBMISSION,
    "evaluation.submit": SeasonPhase.EVALUATION,
    "bootcamp.session.create": SeasonPhase.BOOTCAMP,
    "incubation.assign_mentor": SeasonPhase.INCUBATION,
    "candecidebootcamp.manage": SeasonPhase.BOOTCAMP,
    "evaluation_decision.manage": SeasonPhase.EVALUATION,
}




#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\Permission check\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def has_permission(user, permission_code):
    if not user or not user.is_authenticated:
        return False

    if "ADMIN" in user.role_codes:
        return True

    return permission_code in user.get_permissions()

 #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  Add Phase check\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def can_access(user, permission_code):
    if not has_permission(user, permission_code):
        return False

    required_phase = PHASE_GATED_PERMISSIONS.get(permission_code)

    if required_phase:
        return SeasonPhaseService.is_phase(required_phase)

    return True
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class HasPermission(BasePermission):
    required_permission = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return can_access(request.user, self.required_permission)

# IDEA
class CanSubmitIdea(HasPermission):
    required_permission = "idea.submit"

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CanViewIdea(HasPermission):
    required_permission = "idea.view"


# EVALUATION
class CanEvaluateIdea(HasPermission):
    required_permission = "evaluation.submit"



# BOOTCAMP


# INCUBATION



# ADMIN
class CanManageUsers(HasPermission):
    required_permission = "user.manage"
    
class CanManageSeason(HasPermission):
    required_permission = "season.manage"

class CanManageBootcamp(HasPermission):
    required_permission = "bootcamp.manage"

class CanManageCandidateBootcamp(HasPermission):
    required_permission = "candecidebootcamp.manage"
    
class CanManageEvaluations(HasPermission):
    required_permission = "evaluation.manage"
    
class CanManageEvaluationDecisions(HasPermission):
    required_permission = "evaluation_decision.manage"  