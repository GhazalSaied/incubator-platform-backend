from rest_framework import serializers
from accounts.models import User
from ideas.services.season_phase_service import SeasonPhaseService


class IncubationPhaseSerializer(serializers.Serializer):
    code = serializers.CharField()
    order = serializers.IntegerField()


class IncubationSerializer(serializers.Serializer):
    season = serializers.DictField()
    current_phase = IncubationPhaseSerializer()
    phases = IncubationPhaseSerializer(many=True)


class TeamMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    status = serializers.CharField()


class TeamSerializer(serializers.Serializer):
    has_team = serializers.BooleanField()
    members = TeamMemberSerializer(many=True)

#////////////////////// IDEA OWNER SERIALIZER ///////////////////////


class IdeaOwnerIncubationSerializer(serializers.Serializer):

    def to_representation(self, instance):
        request = self.context["request"]
        user = request.user

        season = SeasonPhaseService.get_current_season()
        current_phase = SeasonPhaseService.get_current_phase(season)

        return {
            "user": {
                "email": user.email,
                "avatar": user.avatar.url if user.avatar else None
            },
            "current_phase": current_phase.phase if current_phase else None,
        }



