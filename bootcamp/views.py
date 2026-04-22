from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.utils.timezone import now
from core.events import EventBus

from .models import BootcampSession, BootcampAbsenceRequest
from .serializers import BootcampSessionSerializer 
from bootcamp.services.absence_service import AbsenceService

from ideas.models import Idea

#/////////////////////////// BOOTCAMP SESSIONS ///////////////////////

class MyBootcampSessionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = BootcampSession.objects.filter(
            phase__phase="BOOTCAMP"
        ).order_by("start_time")

        return Response(BootcampSessionSerializer(sessions, many=True).data)


#/////////////////////////// NEXT SESSION ///////////////////////////

class NextSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = BootcampSession.objects.filter(
            start_time__gte=now()
        ).order_by("start_time").first()

        if not session:
            return Response({"detail": "لا يوجد جلسة قادمة"})

        return Response(BootcampSessionSerializer(session).data)
    

#////////////////////////// ABSENCE REQUEST /////////////////////////////

class CreateAbsenceRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        reason = request.data.get("reason")

        try:
            absence = AbsenceService.request_absence(
                user=request.user,
                session_id=session_id,
                reason=reason
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response({
            "detail": "تم إرسال الطلب بنجاح"
        }, status=201)
