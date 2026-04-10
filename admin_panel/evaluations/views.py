from rest_framework.views import APIView
from rest_framework.response import Response

from admin_panel.evaluations.services.meeting_service import schedule_meeting
from core.permissions import IsAdminOrSecretary

from ideas.models import Idea
from django.shortcuts import get_object_or_404
from ideas.services.season_phase_service import SeasonPhaseService

from .selectors.assignment_dashboard_selectors import (get_assignment_dashboard_ideas)
from .serializers import (AssignmentDashboardSerializer, EvaluatorInfoSerializer, MeetingDashboardSerializer,SeasonEvaluatorSerializer,AssignEvaluatorsSerializer,SetMeetingSerializer)
from .selectors.volunteer_selectors import (get_available_season_evaluators)
from ideas.services.season_phase_service import SeasonPhaseService
from rest_framework import status
from .selectors.Committee_Meeting_Scheduling_Dashboard import get_idea_evaluators, get_ideas_with_evaluators
from .services.evaluation_assignment_service import (EvaluationAssignmentService)


#\\\\\\عرض المشاريع القبولة بالمعسكر لتعيين مقيمين لها\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class AssignmentDashboardAPIView(APIView):

    

    def get(self, request):

        season = SeasonPhaseService.get_current_season()

        sector = request.query_params.get("sector")
        target_audience = request.query_params.get(
            "target_audience"
        )

        ideas = get_assignment_dashboard_ideas(
            season=season,
            sector=sector,
            target_audience=target_audience
        )

        serializer = AssignmentDashboardSerializer(
            ideas,
            many=True
        )

        return Response(serializer.data)
    
    
#\\\\\\\\\\\\\\عرض المقيمين الحاليين لتعيينهم على الافكار\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


class AvailableEvaluatorsView(APIView):

    def get(self, request):

        season = SeasonPhaseService.get_current_season()

        volunteer_type = request.query_params.get("volunteer_type")

        skills = request.query_params.get("skills")

        evaluators = get_available_season_evaluators(
            season=season,
            volunteer_type=volunteer_type,
            skills=skills,
        )

        serializer = SeasonEvaluatorSerializer(
            evaluators,
            many=True
        )

        return Response(serializer.data)
    
    
#\\\\\\\\\\\\\\\\\\\تعيين مقيمين على فكرة معينة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class AssignEvaluatorsToIdeaView(APIView):

    def post(self, request):

        serializer = AssignEvaluatorsSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        idea_id = serializer.validated_data["idea_id"]

        evaluators_ids = serializer.validated_data["evaluators_ids"]

        season = SeasonPhaseService.get_current_season()

        idea = Idea.objects.get(id=idea_id)

        EvaluationAssignmentService.assign_evaluators_to_idea(
            idea=idea,
            evaluators_ids=evaluators_ids,
            season=season
        )

        return Response(
            {"message": "Evaluators assigned successfully"},
            status=status.HTTP_200_OK
        )
        
        
#\\\\\\\\\\\\\\\\\\\\\\عرض جدول المشاريع لتحديد موعد اللجنة \\\\\\\\\\\\\\\\\\\\\\\\\\\\
class MeetingDashboardAPIView(APIView):

    

    def get(self, request):

        season = SeasonPhaseService.get_current_season()

        sector = request.query_params.get("sector")
        target_audience = request.query_params.get(
            "target_audience"
        )

        ideas = get_ideas_with_evaluators(
            season=season,
            sector=sector,
            target_audience=target_audience
        )

        serializer = MeetingDashboardSerializer(
            ideas,
            many=True
        )

        return Response(serializer.data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين المعينين على فكرة معينة في جدول تحديد موعد اللجنة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class IdeaEvaluatorsAPIView(APIView):

    
    def get(self, request, idea_id):

        idea = get_object_or_404(Idea, id=idea_id)

        assignments = get_idea_evaluators(idea)

        serializer = EvaluatorInfoSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\تحديد موعد اللجنة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class SetMeetingAPIView(APIView):

   

    def post(self, request):

        serializer = SetMeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idea_id = serializer.validated_data["idea_id"]
        date = serializer.validated_data["date"]
        time = serializer.validated_data["time"]

        idea = get_object_or_404(Idea, id=idea_id)

        schedule_meeting(
            idea=idea,
            date=date,
            time=time
        )

        return Response({"message": "Meeting scheduled"})