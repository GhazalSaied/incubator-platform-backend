from rest_framework import serializers
from ideas.models import Idea


class IdeaListSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "owner_name",
            "created_at"
        ]

    def get_owner_name(self, obj):
        return obj.owner.email
    


class IdeaDetailSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source="owner.email")

    class Meta:
        model = Idea
        fields = "__all__"