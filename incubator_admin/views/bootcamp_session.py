from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ideas.phases import get_current_phase
from bootcamp.models import BootcampSession
from incubator_admin.serializers.bootcamp_session import BootcampSessionSerializer,BootcampAttendanceSerializer
from rest_framework.generics import ListAPIView
from ideas.models import Idea
from core.permissions import IsAdminOrSecretary

class BootcampSessionCreateView(APIView):
    permission_classes = [IsAuthenticated,IsAdminOrSecretary]

    def post(self, request):
        session = BootcampSession.objects.create(
            title=request.data.get("title"),
            trainer_id=request.data.get("trainer"),
            date=request.data.get("date"),
            start_time=request.data.get("start_time"),
            end_time=request.data.get("end_time"),
            tasks=request.data.get("tasks"),
            location=request.data.get("location"),
        )
        if BootcampSessionSerializer.is_valid():
            
            # 🔥 ناخد الموسم من البيانات قبل الحفظ
            season = BootcampSessionSerializer.validated_data.get('season')

            # 🔥 تحقق من المرحلة
            phase = get_current_phase(season)

            if not phase or phase.phase != 'bootcamp':
                return Response(
                    {"detail": "ليس وقت المعسكر"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ إذا تمام → نحفظ
            session = BootcampSessionSerializer.save()

            return Response(BootcampSessionSerializer.data, status=status.HTTP_201_CREATED)

        return Response(BootcampSessionSerializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BootcampSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        phase_id = request.query_params.get("phase_id")

        sessions = BootcampSession.objects.all()

        if phase_id:
            sessions = sessions.filter(phase_id=phase_id)

        serializer = BootcampSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    



