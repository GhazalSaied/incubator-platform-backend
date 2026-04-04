from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from ideas.serializers import IdeaListSerializer, IdeaDetailSerializer
from core.permissions import IsAdminOrSecretary

from admin_panel.ideas.services import (
    get_admin_ideas,
    get_idea_detail_queryset
)

#\\\IdeaList\\\\
class IdeaListAPIView(ListAPIView):
    serializer_class = IdeaListSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get_queryset(self):
        return get_admin_ideas(self.request)
    
#\\\\IdeaDetail\\\\\
class IdeaDetailAPIView(RetrieveAPIView):
    serializer_class = IdeaDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    lookup_url_kwarg = "idea_id"

    def get_queryset(self):
        return get_idea_detail_queryset()