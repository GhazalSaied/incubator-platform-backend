from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, ValidationError

from bootcamp.models import BootcampSession
from bootcamp.serializers import BootcampSessionSerializer
from ideas.models import Season
from admin_panel.bootcamp.sessions.services import create_bootcamp_session
from ideas.services.season_phase_service import SeasonPhaseService

#\\\\انشاء جلسة للمعسكر\\\\\\\\
class BootcampSessionCreateView(APIView):

    def post(self, request, season_id):
        permissions = SeasonPhaseService.get_phase_permissions()

        if not permissions["can_add_sessions"]:
            raise ValidationError("لا يمكن إضافة جلسات في هذه المرحلة")

        try:
            season = Season.objects.get(id=season_id)
        except Season.DoesNotExist:
            raise ValidationError("الموسم غير موجود")

        serializer = BootcampSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = create_bootcamp_session(serializer, season)

        return Response(
            BootcampSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )
        
#\\\\\\\عرض الجلسات \\\\\
class BootcampSessionListView(ListAPIView):
    
    serializer_class = BootcampSessionSerializer
    def get_queryset(self):
        phase_id = self.request.query_params.get("phase_id")

        queryset = BootcampSession.objects.select_related('phase', 'trainer')

        if phase_id:
            queryset = queryset.filter(phase_id=phase_id)

        return queryset.order_by("date")