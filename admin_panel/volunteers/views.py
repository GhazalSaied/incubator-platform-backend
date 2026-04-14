
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminOrSecretary, IsDirector
from .services.management_service import VolunteerManagementService
from django.core.exceptions import ValidationError
from ideas.services.season_phase_service import SeasonPhaseService
from .services.query_service import VolunteerQueryService
from ideas.models import Season
from datetime import datetime
from django.utils import timezone
from dateutil import parser
#\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع المعلقة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class PendingVolunteersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        data = VolunteerQueryService.get_volunteers_by_status(
            status="PENDING"
        )

        return Response(data)
    
    
    
#\\\\\\\\\\\\\\\\\\\\\\تفاصيل طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\




class VolunteerDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, volunteer_id):

        data = VolunteerQueryService.get_volunteer_details(
            volunteer_id=volunteer_id
        )

        if not data:
            return Response(
                {"error": "المتطوع غير موجود"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\قبول طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ApproveVolunteerView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def post(self, request, volunteer_id):

        try:
            VolunteerManagementService.approve_volunteer(
                volunteer_id=volunteer_id
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "تم قبول المتطوع بنجاح"})


# ----------------------------------------
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\رفض طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class RejectVolunteerView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def post(self, request, volunteer_id):

        try:
            VolunteerManagementService.reject_volunteer(
                volunteer_id=volunteer_id
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "تم رفض المتطوع"})
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المتطوعين المقبولين \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ \
class ApprovedVolunteersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        data = VolunteerQueryService.get_volunteers_by_status(
            status="APPROVED"
        )

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\إرسال دعوة تقييم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class SendInvitationToVolunteerView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def post(self, request, volunteer_id):

        try:
            invitation = VolunteerManagementService.send_invitation_to_volunteer(
                volunteer_id=volunteer_id,
                description=request.data.get("description"),
                meeting_date=request.data.get("meeting_date"),
                expected_duration=request.data.get("expected_duration"),
                task=request.data.get("task"),
                expertise_field=request.data.get("expertise_field"),
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "message": "تم إرسال الدعوة بنجاح",
            "invitation_id": invitation.id
        })
        
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class EvaluatorsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        try:
            season = SeasonPhaseService.get_current_season()
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        data = VolunteerQueryService.get_evaluators(
            season=season
        )

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ازالة مقيم\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



class RemoveEvaluatorRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request, volunteer_id):

        try:
            result = VolunteerManagementService.remove_evaluator_role(
                volunteer_id=volunteer_id
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": "تم إزالة دور المقيم بنجاح",
            **result
        })