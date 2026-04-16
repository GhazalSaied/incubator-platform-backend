from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.utils import timezone
from django.core.exceptions import ValidationError
from core.events import EventBus

from .models import EvaluationInvitation, EvaluationCriterion ,  EvaluationAssignment
from .serializers import EvaluationSerializer
from ideas.models import Idea
from .services.evaluation_service import EvaluationService




# ////////////////////////////////// CREATE OR UPDATE EVALUATION //////////////////////////////////

class EvaluationCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, idea_id):
        idea = get_object_or_404(Idea, id=idea_id)

        try:
            evaluation = EvaluationService.create_or_update_evaluation(
                user=request.user,
                idea=idea,
                data=request.data
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)


# ////////////////////////////////// SUBMIT EVALUATION //////////////////////////////////

class EvaluationSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, idea_id):
        idea = get_object_or_404(Idea, id=idea_id)

        try:
            EvaluationService.submit_evaluation(
                user=request.user,
                idea=idea
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        return Response({"detail": "تم إرسال التقييم بنجاح"})


# ////////////////////////////////// RESPOND TO INVITATION //////////////////////////////////

class RespondToInvitationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            EvaluationInvitation,
            id=invitation_id,
            user=request.user
        )

        action = request.data.get("action")

        if action not in ["accept", "reject"]:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.status != "PENDING":
            return Response({"detail": "تم الرد مسبقاً"}, status=status.HTTP_400_BAD_REQUEST)

        if action == "accept":
            invitation.status = "ACCEPTED"

            ideas = Idea.objects.filter(season=invitation.season)

            for idea in ideas:
                EvaluationAssignment.objects.get_or_create(
                    evaluator=request.user,
                    idea=idea,
                    season=invitation.season,
                    invitation=invitation,
                    defaults={
                        "meeting_date": invitation.meeting_date
                    }
                )
            # اشعار بقبول الانصمام 
            EventBus.emit(
                "evaluation_invitation_accepted",
                payload={
                    "invitation": invitation,
                },
                actor=request.user,
                action_url="/evaluation-dashboard"
            )

        else:
            invitation.status = "REJECTED"
            
            invitation.responded_at = timezone.now()
            invitation.save()
           
           #اشعار برفض الانضمام الى اللجنة
            EventBus.emit(
                "evaluation_invitation_rejected",
                payload={
                    "invitation": invitation,
                },
                actor=request.user,
                action_url="/invitations"
            )

        return Response({"detail": "تم تحديث الحالة"})


# ////////////////////////////////// MY ASSIGNMENTS //////////////////////////////////

class MyAssignmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = EvaluationService.get_user_assignments_data(request.user)
        return Response(data)


# ////////////////////////////////// ASSIGNMENT DETAIL //////////////////////////////////

class AssignmentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assignment_id):
        assignment = EvaluationService.get_assignment_detail(
            request.user,
            assignment_id
        )

        idea = assignment.idea

        data = {
            "title": idea.title,
            "description": idea.description,
            "sector": idea.category,
            "meeting_date": assignment.meeting_date,
        }

        return Response(data)


# ////////////////////////////////// DASHBOARD //////////////////////////////////

class EvaluationDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = EvaluationService.get_dashboard(request.user)
        return Response(data)


# ////////////////////////////////// CRITERIA //////////////////////////////////

class EvaluationCriteriaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        criteria = EvaluationCriterion.objects.filter(
            is_active=True
        ).order_by("order")

        data = [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "max_score": c.max_score
            }
            for c in criteria
        ]

        return Response(data)


# ////////////////////////////////// MY EVALUATION DETAIL //////////////////////////////////

class MyEvaluationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, idea_id):
        evaluation = EvaluationService.get_user_evaluation_detail(
            request.user,
            idea_id
        )

        if not evaluation:
            return Response({"detail": "لا يوجد تقييم"}, status=404)

        return Response(evaluation)
    
#///////////////////////////// INVITATION DETAILS //////////////

class MyInvitationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invitations = EvaluationInvitation.objects.filter(
            user=request.user
        ).order_by("-created_at")

        data = [
            {
                "id": i.id,
                "season": i.season.name,
                "expertise_field": i.expertise_field,
                "meeting_date": i.meeting_date,
                "expected_duration": i.expected_duration,
                "status": i.status,
            }
            for i in invitations
        ]

        return Response(data)
    
#////////////////////// EVALUATION PROGRESS  > كم فكرة عنده / كم خلص /كم باقي //////////

class EvaluationProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assignments = EvaluationAssignment.objects.filter(
            evaluator=request.user
        )

        total = assignments.count()
        completed = assignments.filter(is_completed=True).count()

        return Response({
            "total": total,
            "completed": completed,
            "remaining": total - completed
        })