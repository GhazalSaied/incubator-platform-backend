from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from django.shortcuts import get_object_or_404

from ideas.models import Season
from core.permissions import IsDirector

from ideas.serializers.seasons import (
    SeasonCreateSerializer,
    SeasonSerializer
)

from admin_panel.seasons.services import (
    create_season,
    publish_season,
    close_season
)

from rest_framework.exceptions import PermissionDenied
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase


#\\\\\Create Season\\\
class SeasonCreateView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def post(self, request):
        serializer = SeasonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        season = create_season(serializer.validated_data)

        return Response(
            SeasonSerializer(season).data,
            status=status.HTTP_201_CREATED
        )
        
#\\\\\\Publish Season\\\\
class SeasonPublishView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def post(self, request, pk):
        publish_season(pk)

        return Response(
            {"message": "تم نشر الموسم بنجاح"},
            status=status.HTTP_200_OK
        )
        
        
#\\\\\\\Close Season\\\\
class CloseSeasonAPIView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def post(self, request, season_id):
        try:
            close_season(season_id)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response({
            "detail": "تم إغلاق الموسم وبدء مرحلة المعسكر"
        })
        
        
#\\\\\List\\\\
class SeasonListAPIView(ListAPIView):
    serializer_class = SeasonSerializer
    permission_classes = [IsAuthenticated, IsDirector]

    def get_queryset(self):
        return Season.objects.all().order_by("-id")
    
#\\\\\Detail + Update\\\\
class SeasonDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = SeasonSerializer
    permission_classes = [IsAuthenticated, IsDirector]
    lookup_url_kwarg = "season_id"

    def get_queryset(self):
        return Season.objects.all()

    def update(self, request, *args, **kwargs):

        if not SeasonPhaseService.is_phase(SeasonPhase.SUBMISSION):
            raise PermissionDenied("يمكن تعديل الموسم فقط خلال مرحلة التقديم")

        return super().update(request, *args, **kwargs)