from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from django.shortcuts import get_object_or_404
from rest_framework.generics import UpdateAPIView
from ideas.serializers import SeasonUpdateSerializer
from core.permissions import CanManageSeason,sharedPermissions
from .services.season_query_service import SeasonQueryService
from .services.season_admin_service import SeasonAdminService
from ideas.models import Season, SeasonStatus

from rest_framework.exceptions import ValidationError
from ideas.serializers import (
    SeasonCreateSerializer,SeasonDetailsSerializer
)



from rest_framework.exceptions import PermissionDenied
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase



#\\\\\\\\\\\\\\انشاء موسم\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class CreateSeasonAPIView(APIView):
    permission_classes = [IsAuthenticated, sharedPermissions]
   
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

    permission_classes = [
        IsAuthenticated,
        sharedPermissions
    ]

    def post(self, request, pk):
        season = get_object_or_404(
            Season,
            pk=pk
        )

        SeasonAdminService.publish_season(
            season
        )

        return Response({
            "message": "تم نشر الموسم وفتح باب التقديم"
        })
        
#\\\\\\\Close Season\\\\
class CloseSubmissionAPIView(APIView):
    
    permission_classes = [IsAuthenticated, sharedPermissions]
    def post(self, request, season_id):

        season = get_object_or_404(Season, id=season_id)

        SeasonAdminService.close_submissions(season)

        return Response({
            "message": "تم إغلاق التقديم والانتقال إلى مرحلة المعسكر"
        })
        
#\\\\\List\\\\
class SeasonListAPIView(APIView):
    permission_classes = [IsAuthenticated, sharedPermissions]
    def get(self, request):

        data = SeasonQueryService.list_seasons()

        return Response(data)
#\\\\\Detail\\\\
class SeasonDetailsAPIView(APIView):

    permission_classes = [IsAuthenticated, sharedPermissions]

    def get(self, request, pk):
        season = get_object_or_404(Season, pk=pk)

        ordering = request.query_params.get("ordering")

        data = SeasonQueryService.get_season_details(
            season,
            ordering=ordering
        )

        serializer = SeasonDetailsSerializer(data)

        return Response(serializer.data)
    


from rest_framework.exceptions import ValidationError

class SeasonUpdateView(UpdateAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def perform_update(self, serializer):
        season = self.get_object()

        if season.status == SeasonStatus.CLOSED:
            raise ValidationError({
            "detail": "لا يمكن تعديل موسم مغلق"
        })

        serializer.save()