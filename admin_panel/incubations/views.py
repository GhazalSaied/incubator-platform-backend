from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from admin_panel.seasons.services.season_admin_service import SeasonAdminService
from core.permissions import CanManageIncubation, CanManageIncubationDecisions,sharedIncubationPermissions,sharedPermissions
from ideas.serializers import IdeaDetailSerializer
from .services import GraduationQueryService, GraduationService, IncubationDashboardService, IncubationNotesService, IncubationQueryService,IncubationAssignmentService,IncubationMeetingService
from rest_framework.permissions import IsAuthenticated
from ideas.models import Idea
from rest_framework import status
from django.core.exceptions import ValidationError
from ideas.services import season_phase_service
from rest_framework.generics import ListAPIView
from ideas.services.season_phase_service import SeasonPhaseService


#\\\\\\\\\\\\\\\\\\عرض المشاريع المحتضنة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class IncubationProjectsView(APIView):
    permission_classes = [IsAuthenticated,sharedPermissions]
    def get(self, request):
        data = IncubationDashboardService.get_projects()
        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



class IdeaMentorsView(APIView):
    permission_classes = [IsAuthenticated,sharedPermissions]

    def get(self, request, idea_id):

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response({"error": "الفكرة غير موجودة"}, status=404)

        data = IncubationQueryService.get_idea_mentors(idea=idea)

        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\حذف مقيمين \\\\\\\\\\\\\\\
    

class RemoveMentorsView(APIView):
    permission_classes = [IsAuthenticated,CanManageIncubationDecisions]
    def post(self, request, idea_id):
    
        mentor_ids = request.data.get("mentor_ids", [])

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response(
                {"error": "الفكرة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            result = IncubationAssignmentService.remove_mentors(
                idea=idea,
                mentor_ids=mentor_ids
            )

        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": "تم حذف المقيمين بنجاح",
            "deleted_count": result["deleted_count"]
        })
        

    
#\\\\\\\\\\\\\\\\\\\\\\\\\تعيين مقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class AssignMentorsView(APIView):
    
    permission_classes = [IsAuthenticated,CanManageIncubationDecisions]
    def post(self, request, idea_id):

        mentor_user_ids = request.data.get("mentor_user_ids", [])

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response(
                {"error": "الفكرة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )

        season = season_phase_service.SeasonPhaseService.get_current_season()

        if not season:
            return Response(
                {"error": "لا يوجد موسم حالي"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = IncubationAssignmentService.assign_mentors(
                idea=idea,
                mentor_user_ids=mentor_user_ids,
                season=season
            )

        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": "تم التعيين بنجاح",
            "assigned_count": result["assigned_count"],
            "skipped": result["skipped"]
        })
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\جدولة جلسة متابعة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class  ScheduleMeetingView(APIView):

    permission_classes = [IsAuthenticated,sharedIncubationPermissions]
    def post(self, request, idea_id):
        idea = get_object_or_404(
            Idea,
            id=idea_id
        )

        date = request.data.get("date")
        time = request.data.get("time")

        review = IncubationMeetingService.schedule_meeting(
            idea=idea,
            date=date,
            time=time,
            created_by=request.user
        )

        return Response(
            {
                "detail": "تم تحديد موعد لجنة الاحتضان بنجاح",
                "idea_id": idea.id,
                "meeting_date": review[0].meeting_date if review else None
            },
            status=status.HTTP_200_OK
        )
        

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض ملاحظات اخر جلسة\\\\\\\\\\\\\\\\\\\\\\

class IdeaLatestReviewView(APIView):
    permission_classes = [IsAuthenticated,CanManageIncubation]

    def get(self, request, idea_id):

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response(
                {"error": "الفكرة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )

        data = IncubationNotesService.get_latest_review_notes(
            idea=idea
        )

        return Response(data)
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تخريج فكرة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class GraduateIdeaView(APIView):
    permission_classes = [IsAuthenticated,CanManageIncubationDecisions]
    
    def post(self, request, idea_id):

        action = request.data.get("action")  # positive / negative

        idea = get_object_or_404(Idea, id=idea_id)

        try:
            if action == "positive":
                GraduationService.graduate_positive(idea=idea)

            elif action == "negative":
                GraduationService.graduate_negative(idea=idea)

            else:
                return Response(
                    {"error": "نوع العملية غير صحيح"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": "تم تحديث حالة الفكرة بنجاح",
            "status": idea.status
        }, status=status.HTTP_200_OK)
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class GraduatedProjectsView(APIView):

    #permission_classes = [IsAuthenticated,CanManageIncubation]
    def get(self, request):

        search = request.query_params.get("search")
        category = request.query_params.get("category")

        data = (
            GraduationQueryService
            .list_graduated_projects(
                search=search,
                category=category
            )
        )

        return Response(data)