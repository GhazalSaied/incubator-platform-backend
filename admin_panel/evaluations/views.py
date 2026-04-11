from rest_framework.views import APIView
from rest_framework.response import Response

from .services.evaluation_results_service import EvaluationDecisionService, EvaluationDetailsService, EvaluationResultsService
from .services.EvaluationCriteriaService import EvaluationCriteriaService
from .services.meeting_service import schedule_meeting
from core.permissions import IsAdminOrSecretary, IsDirector
from rest_framework import status
from evaluations.models import EvaluationCriterion
from ideas.models import Idea
from django.shortcuts import get_object_or_404
from ideas.services.season_phase_service import SeasonPhaseService
from rest_framework.permissions import IsAuthenticated
from .selectors.assignment_dashboard_selectors import (get_assignment_dashboard_ideas)
from .serializers import (AssignmentDashboardSerializer, DecisionSerializer, EvaluatorInfoSerializer, MeetingDashboardSerializer,SeasonEvaluatorSerializer,AssignEvaluatorsSerializer,SetMeetingSerializer,EvaluationCriteriaSerializer)
from .selectors.volunteer_selectors import (get_available_season_evaluators)
from ideas.services.season_phase_service import SeasonPhaseService
from rest_framework import status
from .selectors.Committee_Meeting_Scheduling_Dashboard import get_idea_evaluators, get_ideas_with_evaluators
from .services.evaluation_assignment_service import (EvaluationAssignmentService)


#\\\\\\عرض المشاريع القبولة بالمعسكر لتعيين مقيمين لها\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class AssignmentDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    

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
    permission_classes = [IsAuthenticated, IsDirector]

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
    permission_classes = [IsAuthenticated, IsDirector]

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

    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

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

    permission_classes = [IsAuthenticated, IsDirector]
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
    permission_classes = [IsAuthenticated, IsDirector]

   

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

#\\\\\\\\\\\\\\\\\\\\\\\انشاء معيار تقييم\\\\\\\\\\\\\\\\\\\\\\from rest_framework.views import APIView
class CriteriaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):
        criteria = EvaluationCriterion.objects.all()
        serializer = EvaluationCriteriaSerializer(criteria, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EvaluationCriteriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        criteria = EvaluationCriteriaService.create(
            title=serializer.validated_data["title"],
            max_score=serializer.validated_data["max_score"]
        )

        return Response(
            EvaluationCriteriaSerializer(criteria).data,
            status=status.HTTP_201_CREATED
        )
        
        
#\\\\\\\\\\\\\\\\\\\\\\\تعديل معيار تقييم\\\\\\\\\\\\\\\\\\\\\\

class CriteriaUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def put(self, request, pk):
        criteria = get_object_or_404(EvaluationCriterion, pk=pk)

        serializer = EvaluationCriteriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        criteria = EvaluationCriteriaService.update(
            criteria=criteria,
            title=serializer.validated_data.get("title"),
            max_score=serializer.validated_data.get("max_score"),
        )

        return Response(EvaluationCriteriaSerializer(criteria).data)

#\\\\\\\\\\\\\\\\\\\\\\\\تفعيل/تعطيل معيار تقييم\\\\\\\\\\\\\\\\\\\\\\
class CriteriaToggleActiveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request, pk):
        criteria = get_object_or_404(EvaluationCriterion, pk=pk)

        criteria = EvaluationCriteriaService.toggle_active(criteria=criteria)

        return Response(EvaluationCriteriaSerializer(criteria).data)
    
#\\\\\\\\\\\\\\\\\\\\\معاينة نموذج التقييم\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class CriteriaPreviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]


    def get(self, request):

        criteria = EvaluationCriteriaService.get_active_criteria()

        serializer = EvaluationCriteriaSerializer(criteria, many=True)

        return Response(serializer.data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\نشر معايير التقييم\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class PublishCriteriaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request):

        EvaluationCriteriaService.publish()

        return Response({
            "message": "تم نشر النموذج"
        })



#\\\\\\\\\\\\\\\\\\\\\\\\جدول عرض نتائج التقييمات\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class EvaluationResultsView(APIView):
    

    def get(self, request):

        sector = request.query_params.get("sector")
        status = request.query_params.get("status")

        data = EvaluationResultsService.get_results(
            sector=sector,
            status=status
        )

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\عرض المقيمين مع ملاحظاتن\\\\\\\\\\\\\\\\\\\
class EvaluationDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def get(self, request, idea_id):

        idea = get_object_or_404(Idea, id=idea_id)

        data = EvaluationDetailsService.get_idea_evaluation_details(
            idea=idea
        )

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول فكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class AcceptIdeaView(APIView):
    

    def post(self, request, idea_id):

        idea = get_object_or_404(Idea, id=idea_id)

        serializer = DecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        EvaluationDecisionService.accept_idea(
            idea=idea,
            message=serializer.validated_data["message"]
        )

        return Response({"message": "تم قبول الفكرة"})
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\رفض فكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class RejectIdeaView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def post(self, request, idea_id):

        idea = get_object_or_404(Idea, id=idea_id)

        serializer = DecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        EvaluationDecisionService.reject_idea(
            idea=idea,
            message=serializer.validated_data["message"]
        )

        return Response({"message": "تم رفض الفكرة"})