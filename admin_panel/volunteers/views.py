
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import  get_object_or_404
from core.permissions import CanManageVolunteers,sharedPermissions
from .services.management_service import TeamSuggestionService, VolunteerManagementService
from django.core.exceptions import ValidationError
from ideas.services.season_phase_service import SeasonPhaseService
from .services.query_service import VolunteerQueryService
from ideas.models import Season
from datetime import datetime
from django.utils import timezone
from dateutil import parser
#\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع المعلقة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class PendingVolunteersView(APIView):
    
    permission_classes = [IsAuthenticated, CanManageVolunteers]
    def get(self, request):
        
        data = VolunteerQueryService.get_volunteers_by_status(
            status="PENDING"
        )

        return Response(data)
    
    
    
#\\\\\\\\\\\\\\\\\\\\\\تفاصيل طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\




class VolunteerDetailsView(APIView):
  
    permission_classes = [IsAuthenticated, sharedPermissions]
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
 
    permission_classes = [IsAuthenticated, CanManageVolunteers]
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
    
    def get(self, request):
        primary_skills = request.query_params.get("primary_skills")
        data = VolunteerQueryService.get_volunteers_by_status(
            status="APPROVED",
            primary_skills=primary_skills
        )

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\إرسال دعوة تقييم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class SendInvitationToVolunteerView(APIView):
    permission_classes = [IsAuthenticated, sharedPermissions]
    def post(self, request, volunteer_id):

        try:
            invitation = VolunteerManagementService.send_invitation_to_volunteer(
                volunteer_id=volunteer_id,
                description=request.data.get("description"),
                expected_duration=request.data.get("expected_duration"),
                task=request.data.get("task"),
                actor=request.user
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "message": "تم إرسال الدعوة بنجاح",
            "invitation_id": invitation.id
        })
        
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class EvaluatorsView(APIView):
    permission_classes = [IsAuthenticated, sharedPermissions]
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
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات الفريق\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class TeamRequestOwnersAPIView(APIView):

    def get(self, request):

        season_id = request.query_params.get("season")

        season = None
        if season_id:
            season = get_object_or_404(Season, id=season_id)

        data = VolunteerQueryService.get_idea_owners_with_team_requests(
            season=season
        )

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class TeamRequestDetailsAPIView(APIView):


    def get(self, request, pk):

        data = VolunteerQueryService.get_team_request_details(
            request_id=pk
        )

        return Response(data)
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المتطوعين لاقتراحهم لطلب فريق \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   
class AvailableApprovedVolunteersView(APIView):

    def get(self, request):

        data = (
            VolunteerQueryService
            .get_available_approved_volunteers()
        )

        return Response(data)
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اقتراح متطوعين لطلب فريق \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   
class SuggestVolunteersAPIView(APIView):

    def post(self, request, team_request_id):

        volunteer_ids = request.data.get("volunteer_ids", [])

        try:
            data = TeamSuggestionService.suggest_volunteers(
                team_request_id=team_request_id,
                volunteer_ids=volunteer_ids,
                actor=request.user
            )

        except ValidationError as e:

            detail = e.detail

            if isinstance(detail, list):
                detail = detail[0]

            return Response(
                {
                    "error": str(detail)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data,
            status=status.HTTP_200_OK
        )