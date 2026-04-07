from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from ideas.models import Season,Idea
from ideas.serializers import IdeaDetailSerializer,SeasonReviewSerializer
from core.permissions import IsAdminOrSecretary
from django.shortcuts import get_object_or_404
from admin_panel.seasons.services import SeasonAdminService
from rest_framework.response import Response



class SeasonReviewAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, pk):
        ordering = request.query_params.get("ordering")

        season = get_object_or_404(Season, pk=pk)

        data = SeasonAdminService.get_review_submissions_data(
            season,
            ordering
        )

        serializer = SeasonReviewSerializer(instance=data)

        return Response(serializer.data)
    
#\\\\IdeaDetail\\\\\
class IdeaDetailsAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, pk):
        idea = get_object_or_404(
            Idea.objects.select_related("owner", "season")
            .prefetch_related("season__form__questions__choices"),
            pk=pk
        )

        # 🔥 البيانات الأساسية (Serializer تبعك)
        idea_data = IdeaDetailSerializer(idea).data

        # 🔥 الفورم (Service)
        answers = SeasonAdminService.get_idea_details_with_form(idea)

        return Response({
            "idea": idea_data,
            "form_answers": answers
        })