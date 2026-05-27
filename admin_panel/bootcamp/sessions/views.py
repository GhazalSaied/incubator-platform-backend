from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, ValidationError

from bootcamp.models import BootcampSession
from bootcamp.serializers import BootcampSessionsTableSerializer,BootcampSessionCreateSerializer
from core.permissions import CanManageBootcamp, CanManageCandidateBootcamp
from ideas.models import Season
from admin_panel.bootcamp.sessions.services import create_bootcamp_session
from ideas.services.season_phase_service import SeasonPhaseService

#\\\\انشاء جلسة للمعسكر\\\\\\\\
class BootcampSessionCreateView(APIView):
    permission_classes = [IsAuthenticated, CanManageCandidateBootcamp]
    def post(self, request, season_id):
    
        try:
            season = Season.objects.get(id=season_id)
        except Season.DoesNotExist:
            raise ValidationError("الموسم غير موجود")

        serializer = BootcampSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = create_bootcamp_session(serializer, season)

        return Response(
            BootcampSessionsTableSerializer(session).data,
            status=status.HTTP_201_CREATED
        )
        
#\\\\\\\عرض الجلسات \\\\\
class BootcampSessionListView(ListAPIView):
    permission_classes = [IsAuthenticated, CanManageBootcamp]
    serializer_class = BootcampSessionsTableSerializer
    def get_queryset(self):
        phase_id = self.request.query_params.get("phase_id")

        queryset = BootcampSession.objects.select_related('phase', 'trainer')

        if phase_id:
            queryset = queryset.filter(phase_id=phase_id)

        return queryset.order_by("date")