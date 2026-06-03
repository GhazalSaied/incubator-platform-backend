from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from admin_panel.bootcamp.services import SeasonManagementService
from rest_framework import status
from bootcamp.serializers import (
    BootcampIdeaListSerializer,
    BootcampDecisionSerializer
)
from django.db import transaction
from admin_panel.bootcamp.decisions.services import (
    BootcampIdeaQueryService,
    end_bootcamp_sessions,
    process_bootcamp_decision
)
from core.permissions import CanManageBootcamp, CanManageCandidateBootcamp
from ideas.models import Season
from ideas.services.season_phase_service import SeasonPhaseService

#\\\\\\\\\BootcampIdeasList\\\\\
class BootcampIdeasListView(APIView):
    
    parser_classes = [IsAuthenticated, CanManageBootcamp]
    def get(self, request):
        search = request.query_params.get("search")

        data = BootcampIdeaQueryService.list_bootcamp_ideas(search)

        return Response(data)
    
#\\\\\\\BootcampDecision\\\\\\\\\

class BootcampDecisionView(APIView):
    permission_classes = [IsAuthenticated, CanManageCandidateBootcamp]
    def post(self, request, idea_id):

        serializer = BootcampDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idea = process_bootcamp_decision(
            idea_id=idea_id,
            decision=serializer.validated_data["decision"],
            actor=request.user
        )

        return Response(
            {
                "detail": "تم اتخاذ القرار بنجاح",
                "idea_id": idea.id,
                "status": idea.status
            },
            status=status.HTTP_200_OK
        )
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اعلان انتهاء جلسات المعسكر\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  
class EndBootcampSessionsView(APIView):
    
    @transaction.atomic
    def post(self, request, season_id):
        try:
            season = Season.objects.get(id=season_id)
        except Season.DoesNotExist:
            raise ValidationError("الموسم غير موجود")

    
        result = end_bootcamp_sessions(
            season=season,
            actor=request.user
        )

        
        return Response(
            {
                "detail": "تم إنهاء جلسات البوتكامب بنجاح",
                "season_id": season.id
            },
            status=status.HTTP_200_OK
        )