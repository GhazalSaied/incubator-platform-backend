from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.utils.timezone import now
from core.events import EventBus

from .models import BootcampSession, BootcampAbsenceRequest
from .serializers import BootcampSessionSerializer

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
        idea = Idea.objects.get(owner=request.user)

        session_id = request.data.get("session")
        reason = request.data.get("reason")

        absence = BootcampAbsenceRequest.objects.create(
            idea=idea,
            session_id=session_id,
            reason=reason
        )
        EventBus.emit("absence_requested", {
            "idea": idea,
            "user": request.user,
            "session_id": session_id,
            "action_url": "/bootcamp"
        })       
        return Response({"detail": "تم إرسال الطلب"})
