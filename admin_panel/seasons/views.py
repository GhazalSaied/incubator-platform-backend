from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from django.shortcuts import get_object_or_404

from ideas.models import Season
from core.permissions import IsDirector,IsAdminOrSecretary

from ideas.serializers import (
    SeasonCreateSerializer,SeasonListSerializer,SeasonDetailsSerializer
)

from admin_panel.seasons.services import SeasonAdminService



from rest_framework.exceptions import PermissionDenied
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase



#\\\\\\\\\\\\\\انشاء موسم\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class CreateSeasonAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request):

        serializer = SeasonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        season = SeasonAdminService.create_season(
            serializer.validated_data
        )

        return Response({
            "id": season.id
        })
#\\\\\\Publish Season\\\\

class PublishSeasonAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    def post(self, request, pk):
        season = get_object_or_404(Season, pk=pk)

        SeasonAdminService.publish_season(season)

        return Response({
            "message": "تم نشر الموسم وفتح باب التقديم"
        })
        
        
#\\\\\\\Close Season\\\\
class CloseSubmissionAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request, season_id):

        season = get_object_or_404(Season, id=season_id)

        SeasonAdminService.close_submissions(season)

        return Response({
            "message": "تم إغلاق التقديم والانتقال إلى مرحلة المعسكر"
        })
        
#\\\\\List\\\\
class SeasonListAPIView(APIView):
    
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):
        year = request.query_params.get("year")

        data = SeasonAdminService.list_seasons(year)

        serializer = SeasonListSerializer(data, many=True)

        return Response(serializer.data)
    
#\\\\\Detail + Update\\\\
class SeasonDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, pk):
        season = get_object_or_404(Season, pk=pk)

        data = SeasonAdminService.get_season_details(season)

        serializer = SeasonDetailsSerializer(data)

        return Response(serializer.data)