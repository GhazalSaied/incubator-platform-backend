from rest_framework import serializers
from ideas.models import IdeaForm, Season


class IdeaFormSerializer(serializers.ModelSerializer):
    season_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IdeaForm
        fields = ['id', 'title', 'season_id']

    def validate_season_id(self, value):
        if not Season.objects.filter(id=value).exists():
            raise serializers.ValidationError("الموسم غير موجود.")
        return value

    def validate(self, attrs):
        season_id = attrs['season_id']
        if IdeaForm.objects.filter(season_id=season_id).exists():
            raise serializers.ValidationError(
                "يوجد فورم لهذا الموسم مسبقاً."
            )
        return attrs

    def create(self, validated_data):
        season_id = validated_data.pop('season_id')
        season = Season.objects.get(id=season_id)

        return IdeaForm.objects.create(
            season=season,
            **validated_data
        )
