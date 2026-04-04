from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from core.permissions import IsAdminOrSecretary

from bootcamp.models import BootcampSession
from bootcamp.serializers import BootcampSessionSerializer

from admin_panel.bootcamp.sessions.services import create_bootcamp_session

#\\\\انشاء جلسة للمعسكر\\\\\\\\
class BootcampSessionCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request):
        serializer = BootcampSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = create_bootcamp_session(serializer)

        return Response(
            BootcampSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )
        
        
        
#\\\\\\\عرض الجلسات \\\\\
class BootcampSessionListView(ListAPIView):
    serializer_class = BootcampSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        phase_id = self.request.query_params.get("phase_id")

        queryset = BootcampSession.objects.select_related("trainer", "season")

        if phase_id:
            queryset = queryset.filter(phase_id=phase_id)

        return queryset.order_by("date")