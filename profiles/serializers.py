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


class IdeaOwnerProfileSerializer(serializers.Serializer):
    user = serializers.DictField()
    incubation = IncubationSerializer()
    team = TeamSerializer()
    consultations = serializers.DictField()

    def to_representation(self, instance):
        request = self.context["request"]
        user = request.user

        season = SeasonPhaseService.get_current_season()
        current_phase = SeasonPhaseService.get_current_phase(season)
        phases = season.phases.all().order_by("order")

        return {
            "user": {
                "email": user.email,
                "avatar": user.avatar.url if user.avatar else None
            },
            "incubation": {
                "season": {
                    "id": season.id,
                    "name": season.name
                },
                "current_phase": {
                    "code": current_phase.phase,
                    "order": current_phase.order
                },
                "phases": [
                    {
                        "code": phase.phase,
                        "order": phase.order
                    }
                    for phase in phases
                ]
            },
            "team": {
                "has_team": False,
                "members": []
            },
            "consultations": {
                "enabled": True
            }
        }



