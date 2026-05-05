from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from ideas.models import Season,Idea
from ideas.serializers import IdeaDetailSerializer, ProjectDetailsSerializer,SeasonReviewSerializer
from django.shortcuts import get_object_or_404
from admin_panel.seasons.services.season_admin_service import SeasonAdminService
from admin_panel.seasons.services.season_query_service import SeasonQueryService
from rest_framework.response import Response
from rest_framework.views import APIView


class SeasonReviewAPIView(ListAPIView):
    

    def get(self, request, pk):
        ordering = request.query_params.get("ordering")

        season = get_object_or_404(Season, pk=pk)

        data = SeasonQueryService.get_review_submissions_data(
            season,
            ordering
        )

        serializer = SeasonReviewSerializer(instance=data)

        return Response(serializer.data)
    

#\\\\\\\\\\\\\\\\\\\   IDEA DETAILS \\\\\\\\\\\\\\\\\\

class IdeaDetailsAPIView(APIView):

    def get(self, request, pk):
        idea = Idea.objects.get(pk=pk)

        serializer = ProjectDetailsSerializer(idea)

        # 🔥 جلب أعضاء الفريق
        team_members = idea.team_members.select_related("user").all()

        team_data = [
            {
                "name": member.user.full_name,
                "email": member.user.email
            }
            for member in team_members
        ]

        # 🔥 دمج البيانات
        response_data = serializer.data
        response_data["team_members"] = team_data

        return Response(response_data)