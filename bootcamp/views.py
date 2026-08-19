from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from core.events import EventBus

from .models import BootcampSession, BootcampAbsenceRequest
from .serializers import (  BootcampSessionsTableSerializer,
                            NextBootcampSessionSerializer,
                            BootcampAbsenceRequestCreateSerializer,
                            VolunteerBootcampSessionSerializer,
                            BootcampIdeaAttendanceListSerializer,
                            BootcampAttendanceCreateSerializer,
                           )

from bootcamp.services.absence_service import AbsenceService
from ideas.models import Idea
from core.permissions import CanViewBootcamp,CanSubmitBootcampAbsence
from bootcamp.services.bootcamp_service import VolunteerBootcampService
from .services.bootcamp_owner_service import (
    BootcampOwnerService,
)

#/////////////////////////// BOOTCAMP SESSIONS ///////////////////////

class OwnerBootcampSessionsAPIView(APIView):
    permission_classes = [IsAuthenticated,CanViewBootcamp]

    def get(self, request):
        try:
            BootcampOwnerService.get_user_bootcamp_idea(
                user=request.user
            )
        except ValidationError as e:
            return Response(
                {
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        sessions = BootcampOwnerService.get_all_bootcamp_sessions()

        serializer = BootcampSessionsTableSerializer(
            sessions,
            many=True
        )

        return Response(
            {
                
                "results": serializer.data,
            },
            status=status.HTTP_200_OK
        )



#/////////////////////////// NEXT SESSION ///////////////////////////

class OwnerNextBootcampSessionAPIView(APIView):
    permission_classes = [IsAuthenticated,CanViewBootcamp]

    def get(self, request):
        try:
            BootcampOwnerService.get_user_bootcamp_idea(
                user=request.user
            )
        except ValidationError as e:
            return Response(
                {
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        session = BootcampOwnerService.get_next_session()

        if not session:
            return Response(
                {
                    "message": "لا يوجد جلسة قادمة"
                },
                status=status.HTTP_200_OK
            )

        serializer = NextBootcampSessionSerializer(
            session
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


#////////////////////////// ABSENCE REQUEST /////////////////////////////

class CreateBootcampAbsenceRequestAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        CanSubmitBootcampAbsence
    ]

    def post(self, request):
        serializer = BootcampAbsenceRequestCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            BootcampOwnerService.create_absence_request(
                user=request.user,
                reason=serializer.validated_data["reason"],
            )

        except ValidationError as e:
            detail = e.detail

            if isinstance(detail, list):
                message = detail[0]
            elif isinstance(detail, dict):
                message = next(iter(detail.values()))[0]
            else:
                message = str(detail)

            return Response(
                {
                    "message": message
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "تم إرسال طلب الغياب بنجاح"
            },
            status=status.HTTP_201_CREATED
        )

#//////////////////////////// VOLUNTEER BOOTCAMP SESSIONS > TRAINER ////////////////////


class MyAssignedBootcampSessionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = VolunteerBootcampService.get_my_sessions(
            user=request.user
        )

        serializer = VolunteerBootcampSessionSerializer(
            sessions,
            many=True
        )

        return Response(
            {
               
                "results": serializer.data,
            },
            status=status.HTTP_200_OK
        )
    
#/////////////////////////// BOOTCAMP IDEA ATTENDANCE LIST ////////////////

class BootcampSessionIdeasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = VolunteerBootcampService.get_session_or_none(
            session_id=session_id
        )

        if not session:
            return Response(
                {
                    "message": "Session not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if session.trainer_id != request.user.id:
            return Response(
                {
                    "message": "You are not allowed to access this session."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        ideas = VolunteerBootcampService.get_pending_bootcamp_ideas_for_session(
            session=session
        )

        serializer = BootcampIdeaAttendanceListSerializer(
            ideas,
            many=True
        )

        return Response(
            {
               
                "results": serializer.data,
            },
            status=status.HTTP_200_OK
        )

#/////////////////////////// BOOTCAMP IDEA ATTENDANCE CREATE ///////////////

class CreateBootcampAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = VolunteerBootcampService.get_session_or_none(
            session_id=session_id
        )

        if not session:
            return Response(
                {
                    "message": "Session not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BootcampAttendanceCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "session": session,
            }
        )

        serializer.is_valid(raise_exception=True)

        VolunteerBootcampService.create_attendance(
            session=session,
            idea=serializer.validated_data["idea"],
            status=serializer.validated_data["status"],
            marked_by=request.user,
        )

        return Response(
            {
                "message": "Attendance submitted successfully."
            },
            status=status.HTTP_201_CREATED
        )