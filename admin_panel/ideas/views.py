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
      
        idea_id = idea.id
        specialization = idea.answers.get("الاختصاص", "غير محدد")
        sector = idea.sector
        expected_duration = idea.answers.get("المدة المتوقعة لانجاز المشروع")
        team_names = idea.answers.get("اسماء اعضاء الفريق", [])
        team_emails = idea.answers.get("ايميلات اعضاء الفريق", [])

        if isinstance(team_names, str):
            team_names = team_names.split(",")

        if isinstance(team_emails, str):
            team_emails = team_emails.split(",")

        team_members = [
            {"name": team_names[i] if i < len(team_names) else "",
            "email": team_emails[i] if i < len(team_emails) else ""}
            for i in range(max(len(team_names), len(team_emails)))
        ]

        response_data = serializer.data
        response_data["team_members"] = team_members
        response_data["sector"] = sector
        response_data["specialization"] = specialization
        response_data["expected_duration"] = expected_duration or "غير محدد"
        response_data["idea_id"] = idea_id
        return Response(response_data)