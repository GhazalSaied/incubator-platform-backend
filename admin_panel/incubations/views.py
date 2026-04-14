from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from admin_panel.seasons.services import SeasonAdminService
from core.permissions import IsAdminOrSecretary,IsDirector
from ideas.serializers import IdeaDetailSerializer
from .services import IncubationDashboardService, IncubationNotesService, IncubationQueryService,IncubationAssignmentService,IncubationMeetingService
from rest_framework.permissions import IsAuthenticated
from ideas.models import Idea
from rest_framework import status
from django.core.exceptions import ValidationError
from ideas.services import season_phase_service
from rest_framework.generics import ListAPIView



#\\\\\\\\\\\\\\\\\\عرض المشاريع المحتضنة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class IncubationProjectsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):
        data = IncubationDashboardService.get_projects()
        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



class IdeaMentorsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, idea_id):

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response({"error": "الفكرة غير موجودة"}, status=404)

        data = IncubationQueryService.get_idea_mentors(idea=idea)

        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\حذف مقيمين \\\\\\\\\\\\\\\
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

class RemoveMentorsView(APIView):

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
        
#\\\\\\\\\\\\\\عرض مقيمين لاضافة مقيم\\\\\\\\\\\\\\\\\\\\\\\\\\\


class AvailableEvaluatorsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        specialization = request.query_params.get("specialization")
        fields = request.query_params.get("fields")

        season = season_phase_service.SeasonPhaseService.get_current_season()

        if not season:
            return Response(
                {"error": "لا يوجد موسم حالي"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = IncubationQueryService.get_available_evaluators_data(
            season=season,
            specialization=specialization,
            fields=fields
        )

        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\تعيين مقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class AssignMentorsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

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

class ScheduleMeetingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]


    def post(self, request, idea_id):

        date = request.data.get("date")
        time = request.data.get("time")

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response(
                {"error": "الفكرة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            result = IncubationMeetingService.schedule_meeting(
                idea=idea,
                date=date,
                time=time,
                created_by=request.user)
                        
               

        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": "تم تحديد الموعد وإرسال الإشعارات",
            "meeting_date":  result.meeting_date
        })
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  عرض تفاصيل الفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class IdeaDetailsAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    

    def get(self, request, pk):
        idea = get_object_or_404(
            Idea.objects.select_related("owner", "season")
            .prefetch_related("season__form__questions__choices"),
            pk=pk
        )

        # 🔥 البيانات الأساسية (Serializer تبعك)
        idea_data = IdeaDetailSerializer(idea).data

        # 🔥 الفورم (Service)
        answers = SeasonAdminService.get_idea_details_with_form(idea)

        return Response({
            "idea": idea_data,
            "form_answers": answers
        })
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض ملاحظات اخر جلسة\\\\\\\\\\\\\\\\\\\\\\

class IdeaLatestReviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

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