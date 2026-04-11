from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from admin_panel.bootcamp.services import SeasonManagementService
from core.permissions import IsAdminOrSecretary, IsDirector

from bootcamp.serializers import (
    BootcampIdeaListSerializer,
    BootcampDecisionSerializer
)

from admin_panel.bootcamp.decisions.services import (
    get_bootcamp_ideas,
    process_bootcamp_decision
)
from ideas.models import Season

#\\\\\\\\\BootcampIdeasList\\\\\
class BootcampIdeasListView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]
    
    def get(self, request):
        search = request.query_params.get("search")

        data = get_bootcamp_ideas(search)

        serializer = BootcampIdeaListSerializer(data, many=True)
        return Response(serializer.data)
    
#\\\\\\\BootcampDecision\\\\\\\\\
class BootcampDecisionView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]
    

    def post(self, request):
        serializer = BootcampDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idea = process_bootcamp_decision(
            serializer.validated_data["idea_id"],
            serializer.validated_data["decision"],
            serializer.validated_data["message"]
        )

        return Response({
            "idea_id": idea.id,
            "status": idea.status
        })
        


#\\\\\\\\\\\\\\\\\\\\\اعلان انتهاء مرحلة المعسكر وبداية مرحلة التقييم\\\\\\\\\\\\\\\\\\\\\\\\\\\
class EndCampView(APIView):
    

    def post(self, request, season_id):
        

        season = get_object_or_404(Season, id=season_id)

        SeasonManagementService.end_camp_and_start_evaluation(
            season=season
        )

        return Response({
            "message": "تم إنهاء المعسكر وبدء مرحلة التقييم"
        })