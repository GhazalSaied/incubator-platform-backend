from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
from django.db import models
from ideas.phases import SeasonPhase
from ideas.services.season_phase_service import SeasonPhaseService
from accounts.models import UserRole
from accounts.models import Permission
from rest_framework.permissions import BasePermission


PERMISSIONS = {

    "idea.view": "View Idea",

    #EVALUATION
    "evaluation.submit": "Submit Evaluation",
    "evaluation.center.view": "View Evaluation Center",
    "evaluation.notes.view": "View Evaluation Notes",

    "user.manage": "Manage Users",
    "season.manage": "Manage Season",
    "bootcamp.manage": "Manage Bootcamp",
    "candecidebootcamp.manage": "Manage Candidate Bootcamp",
    "evaluation.manage": "Manage Evaluations",
    "evaluation_decision.manage": "Manage Evaluation Decisions",
    "incubtion.manage": "Manage Incubation",
    "incubtion_decision.manage": "Manage Incubation Decisions",
    "exhibition.manage": "Manage Exhibition",
    "can_decide_exhibition": "Can Decide Exhibition",
    "volunteer.manage": "Manage Volunteers",
    "workshop.manage": "Manage Workshops",
    #VOLUNTEER:
    "workshop.manage": "Manage Workshop",
    "volunteer.requests.manage": "Manage Volunteer Requests",
    "volunteer.assigned_consultations.view": "View Assigned Consultations",
    "volunteer.profile.manage" : "manage volunteer profile",
    "consultants.view" : "View Consultants",

    #INCUBATION
    "team.request_completion": "Request Team Completion",
    "incubation.team_candidates.view": "View Team Candidate Volunteers",
    "incubation.join_request.send": "Send Join Request",
    "incubation_reviews.notes.view" :"View Incubation Reviews Notes",

    #BOOTCAMP
    "bootcamp.view": "View Bootcamp",
    "bootcamp.absence.submit": "Submit Bootcamp Absence",


    # EXHIBITION
    "exhibition.card.create": "Create Exhibition Card",
    "exhibition.card.view": "View Exhibition Card",

    #MESSAGING
    "message.send": "Send Messages",

}
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
PHASE_GATED_PERMISSIONS = {
    
    "evaluation.submit": SeasonPhase.EVALUATION,
    "bootcamp.session.create": SeasonPhase.BOOTCAMP,
    "incubation.assign_mentor": SeasonPhase.INCUBATION,
    "candecidebootcamp.manage": SeasonPhase.BOOTCAMP,
    "evaluation_decision.manage": SeasonPhase.EVALUATION,
    "incubtion_decision.manage": SeasonPhase.INCUBATION,
    "can_decide_exhibition": SeasonPhase.EXHIBITION,

    "bootcamp.view": SeasonPhase.BOOTCAMP,
    "bootcamp.absence.submit": SeasonPhase.BOOTCAMP,



    "team.request_completion": SeasonPhase.INCUBATION,
    "incubation.team_candidates.view": SeasonPhase.INCUBATION,
    "incubation.join_request.send": SeasonPhase.INCUBATION,
    "incubationreviews.assignments.view": SeasonPhase.INCUBATION,
    "incubation_reviews.notes.view":SeasonPhase.INCUBATION,



    "exhibition.card.create": SeasonPhase.EXHIBITION,
    "exhibition.card.view": SeasonPhase.EXHIBITION,
    
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





class CanViewIdea(HasPermission):
    required_permission = "idea.view"


# EVALUATION
class CanEvaluateIdea(HasPermission):
    required_permission = "evaluation.submit"

class CanViewEvaluationCenter(HasPermission):
    required_permission = "evaluation.center.view"


class CanViewEvaluationNotes(HasPermission):
    required_permission = "evaluation.notes.view"



# BOOTCAMP

class CanViewBootcamp(HasPermission):
    required_permission = "bootcamp.view"


class CanSubmitBootcampAbsence(HasPermission):
    required_permission = "bootcamp.absence.submit"


# INCUBATION

class CanRequestTeamCompletion(HasPermission):
    required_permission = "team.request_completion"


class CanViewTeamCandidates(HasPermission):
    required_permission = "incubation.team_candidates.view"


class CanSendJoinRequest(HasPermission):
    required_permission = "incubation.join_request.send"


class CanViewIncubationReviewsNotes(HasPermission):
    required_permission = "incubation_reviews.notes.view"


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
    
class CanManageIncubation(HasPermission):
    required_permission = "incubtion.manage"
    
    
class CanManageIncubationDecisions(HasPermission):
    required_permission = "incubtion_decision.manage"
    
class CanManageExhibition(HasPermission):
    required_permission = "exhibition.manage"
    
class CanDecideExhibition(HasPermission):
    required_permission = "can_decide_exhibition"

class CanManageVolunteers(HasPermission):
    required_permission = "volunteer.manage"
    
class CanManageWorkshops(HasPermission):
    required_permission = "workshop.manage"


#VOLUNTEER :
class CanManageWorkshop(HasPermission):
    required_permission = "workshop.manage"

class CanManageVolunteerRequests(HasPermission):
    required_permission = "volunteer.requests.manage"


class CanViewAssignedConsultations(HasPermission):
    required_permission = "volunteer.assigned_consultations.view"

class CanManageVolunteerProfile(HasPermission):
    required_permission = "volunteer.profile.manage"

class CanViewConsultants(HasPermission):
    required_permission = "consultants.view"


# MESSAGING
class CanSendMessage(HasPermission):
    required_permission = "message.send"

#EXHIBITION

class CanCreateExhibitionCard(HasPermission):
    required_permission = "exhibition.card.create"


class CanViewExhibitionCard(HasPermission):
    required_permission = "exhibition.card.view"

