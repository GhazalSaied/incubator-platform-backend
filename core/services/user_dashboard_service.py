from ideas.services.idea_dashboard_service import IdeaDashboardService
from volunteers.services.volunteer_service import VolunteerService
from ideas.services.idea_service import IdeaService
from ideas.models import TeamMember

from evaluations.models import EvaluationAssignment
from evaluations.services.evaluation_service import EvaluationService

from volunteers.services.volunteer_service import get_workshop_stats, get_next_workshop
from notifications.models import Notification
from notifications.services.notification_service import NotificationService


class UserDashboardService:

    @staticmethod
    def build(user):

        #  Role Detection
        is_idea_owner = user.ideas.exists()
        is_volunteer = hasattr(user, "volunteer_profile")
        is_team_member = TeamMember.objects.filter(user=user).exists()
        is_evaluator = EvaluationAssignment.objects.filter(
            evaluator=user
        ).exists()

        response = {
            "roles": {
                "is_idea_owner": is_idea_owner,
                "is_volunteer": is_volunteer,
                "is_team_member": is_team_member,
                "is_evaluator": is_evaluator,
            }
        }

        #  IDEA DASHBOARD
        if is_idea_owner:
            response["idea_dashboard"] = IdeaDashboardService.build(user)

        #  VOLUNTEER DASHBOARD
        if is_volunteer:
            volunteer_data = VolunteerService.get_dashboard(user)
            next_workshop = get_next_workshop(user)

            response["volunteer_dashboard"] = {
                "profile": volunteer_data["profile"].id,
                "availability_count": len(volunteer_data["availability"]),
                "consultations": volunteer_data["consultations"],

                "workshop_stats": get_workshop_stats(user),

                "next_workshop": {
                    "title": next_workshop.title,
                    "start_date": next_workshop.start_date,
                    "time_from": next_workshop.time_from,
                } if next_workshop else None,
            }

        #  TEAM DASHBOARD
        if is_team_member:
            response["team_dashboard"] = IdeaService.get_team_dashboard(user)

        #  EVALUATOR DASHBOARD
        if is_evaluator:
            response["evaluator_dashboard"] = EvaluationService.get_dashboard(user)

        #  NOTIFICATIONS SUMMARY
        notifications = Notification.objects.filter(user=user)

        response["notifications_summary"] = {
            "total": notifications.count(),
            "unread": notifications.filter(is_read=False).count(),

            # 
            "by_role": {
                "volunteer": notifications.filter(target_role="VOLUNTEER").count(),
                "idea_owner": notifications.filter(target_role="IDEA_OWNER").count(),
                "team_member": notifications.filter(target_role="TEAM_MEMBER").count(),
            }
        }

        return response