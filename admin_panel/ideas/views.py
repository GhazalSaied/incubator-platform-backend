from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from ideas.models import Season,Idea
from ideas.serializers import IdeaDetailSerializer, ProjectDetailsSerializer,SeasonReviewSerializer
from django.shortcuts import get_object_or_404
from admin_panel.seasons.services.season_admin_service import SeasonAdminService
from admin_panel.seasons.services.season_query_service import SeasonQueryService
from rest_framework.response import Response
from rest_framework.views import APIView

    

#\\\\\\\\\\\\\\\\\\\   IDEA DETAILS \\\\\\\\\\\\\\\\\\

class IdeaDetailsAPIView(APIView):

   
    def get(self, request, pk):
        idea = Idea.objects.get(pk=pk)

        serializer = ProjectDetailsSerializer(idea)

        team_members = idea.team_members.select_related("user").all()
        team_data = [
            {
                "name": member.user.full_name,
                "email": member.user.email
            }
            for member in team_members
        ]
        specialization = idea.answers.get("specialization", "غير محدد")
        expected_duration = idea.answers.get("expected_duration")
        response_data = serializer.data
        response_data["team_members"] = team_data
        response_data["specialization"] = specialization
        response_data["expected_duration"] = expected_duration or "غير محدد"
        return Response(response_data)