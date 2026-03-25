from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from ideas.models import Idea
from incubator_admin.serializers.idea import IdeaListSerializer,IdeaDetailSerializer
from core.permissions import IsAdminOrSecretary






class IdeaListAPIView(ListAPIView):
    serializer_class = IdeaListSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get_queryset(self):
        season_id = self.request.query_params.get("season")

        queryset = Idea.objects.all().order_by("-created_at")

        if season_id:
            queryset = queryset.filter(season_id=season_id)

        return queryset
    
    

class IdeaDetailAPIView(RetrieveAPIView):
    serializer_class = IdeaDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    lookup_url_kwarg = "idea_id"

    def get_queryset(self):
        return Idea.objects.all()