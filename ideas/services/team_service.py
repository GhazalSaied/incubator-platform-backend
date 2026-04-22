from core.events import EventBus
from ideas.models import TeamMember, TeamStatus


class TeamService:

    @staticmethod
    def add_member(*, idea, user, team_request=None, added_by=None):

        if TeamMember.objects.filter(idea=idea, user=user).exists():
            return idea

        current_members = TeamMember.objects.filter(idea=idea).count()

        if team_request and current_members >= team_request.members_needed:
            raise Exception("Team is already full")

        TeamMember.objects.create(
            idea=idea,
            user=user
        )

        current_members += 1

        #  status logic
        if team_request:
            if current_members >= team_request.members_needed:
                idea.team_status = TeamStatus.TEAM_FULL
            else:
                idea.team_status = TeamStatus.TEAM_BUILDING
        else:
            idea.team_status = TeamStatus.IN_PROGRESS

        idea.save()

        #  EVENT
        EventBus.emit(
            "team_member_added",
            payload={
                "idea": idea,
                "member": user,
            },
            actor=added_by or user
        )

        #  EVENT (team completed)
        if idea.team_status == TeamStatus.TEAM_FULL:
            EventBus.emit(
                "team_completed",
                payload={
                    "idea": idea,
                },
                actor=added_by or user
            )

     
        return idea
    
    # /////////////// REMOVE MEMBER ////////////////////
     
    @staticmethod
    def remove_member(*, idea, user, removed_by=None):

        member = TeamMember.objects.filter(
            idea=idea,
            user=user
        ).first()

        if not member:
            return idea

        member.delete()

        remaining = TeamMember.objects.filter(idea=idea).count()

        if remaining == 0:
            idea.team_status = TeamStatus.NO_TEAM
        else:
            idea.team_status = TeamStatus.TEAM_BUILDING

        idea.save()

        #  EVENT
        EventBus.emit(
            "team_member_removed",
            payload={
                "idea": idea,
                "member": user,
            },
            actor=removed_by or user
        )

        return idea