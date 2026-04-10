from ideas.services.idea_dashboard_service import IdeaDashboardService
from volunteers.services.volunteer_service import VolunteerService
from ideas.services.idea_service import IdeaService
from ideas.models import TeamMember
from notifications.models import Notification



class UserDashboardService:

    @staticmethod
    def build(user):
        
        # roles detection

        is_idea_owner = user.ideas.exists()
        is_volunteer = hasattr(user, "volunteer_profile")
        is_team_member = TeamMember.objects.filter(user=user).exists()

        response = {
            "roles": {
                "is_idea_owner": is_idea_owner,
                "is_volunteer": is_volunteer,
                "is_team_member": is_team_member,
            }
        }

        # IDEA DASHBOARD

        if is_idea_owner:
            idea_data = IdeaDashboardService.build(user)
            response["idea_dashboard"] = idea_data

        
        # VOLUNTEER DASHBOARD
      
        if is_volunteer:
            volunteer_data = VolunteerService.get_dashboard(user)

            response["volunteer_dashboard"] = {
                "profile": volunteer_data["profile"].id,
                "availability_count": len(volunteer_data["availability"]),
                "consultations": volunteer_data["consultations"]
            }

        # TEAM DASHBOARD
        
        if is_team_member:
            team_data = IdeaService.get_team_dashboard(user)
            response["team_dashboard"] = team_data

        # NOTIFICATIONS SUMMARY
        
        notifications = Notification.objects.filter(user=user)

        response["notifications_summary"] = {
            "total": notifications.count(),
            "volunteer": notifications.filter(target_role="VOLUNTEER").count(),
            "idea_owner": notifications.filter(target_role="IDEA_OWNER").count(),
            "team_member": notifications.filter(target_role="TEAM_MEMBER").count(),
        }

        return response