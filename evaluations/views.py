from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.utils import timezone
from django.core.exceptions import ValidationError
from core.events import EventBus

from .models import EvaluationInvitation, EvaluationCriterion ,  EvaluationAssignment
from .serializers import EvaluationSerializer ,EvaluationNoteSerializer,IncubationReviewSerializer
from ideas.models import Idea
from evaluations.services.evaluation_service import EvaluationService
from ideas.serializers import ProjectDetailsSerializer




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
            invitation.responded_at = timezone.now()
            invitation.save()

            # اشعار بقبول الانصمام 
            EventBus.emit(
                "evaluation_invitation_accepted",
                invitation=invitation,
                actor=request.user,
            )

        else:
            invitation.status = "REJECTED"
            
            invitation.responded_at = timezone.now()
            invitation.save()
           
           #اشعار برفض الانضمام الى اللجنة
            EventBus.emit(
                "evaluation_invitation_rejected",
                invitation=invitation,
                actor=request.user,
            )

        return Response({"detail": "تم تحديث الحالة"})


# ////////////////////////////////// MY ASSIGNMENTS > (Evaluation Center) //////////////////////////////////

class MyAssignmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = EvaluationService.get_user_assignments_data(request.user)
        return Response(data)


# ////////////////////////////////// ASSIGNMENT DETAIL //////////////////////////////////


class AssignmentProjectDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assignment_id):
        resolved_data = EvaluationService.get_assignment_detail(
            request.user,
            assignment_id
        )

        idea = resolved_data["idea"]
        meeting_date = resolved_data["meeting_date"]

        serializer = ProjectDetailsSerializer(idea)

        return Response({
            "meeting_date": meeting_date,
            "project_details": serializer.data
        })



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



#//////////////////////// INVITATION DETAILS ////////////////////////////

class InvitationDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, invitation_id):
        invitation = get_object_or_404(
            EvaluationInvitation,
            id=invitation_id,
            user=request.user
        )

        data = {
            "id": invitation.id,
            "task": invitation.task,
            "expected_duration": invitation.expected_duration,
            "status": invitation.status,
        }

        return Response(data)
    
#///////////////////////// OPEN EVALUATION FORM ////////////////////

class EvaluationFormAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, idea_id):
        idea = get_object_or_404(Idea, id=idea_id)

        data = EvaluationService.get_evaluation_form(
            user=request.user,
            idea=idea
        )

        if not data["is_published"]:
            return Response({
                "is_published": False,
                "message": "الفورم قيد الإنشاء من قبل الإدارة"
            })

        return Response(data)


#/////////////////////// NOTES API (GET+ POST) //////////////////////


class EvaluationNotesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, idea_id):
        idea = get_object_or_404(Idea, id=idea_id)
        notes = EvaluationService.get_evaluation_notes(request.user, idea)
        serializer = EvaluationNoteSerializer(notes, many=True)
        return Response(serializer.data)

    def post(self, request, idea_id):
        idea = get_object_or_404(Idea, id=idea_id)

        note = EvaluationService.add_evaluation_note(
            user=request.user,
            idea=idea,
            note_text=request.data.get("note")
        )

        serializer = EvaluationNoteSerializer(note)
        return Response(serializer.data)
    
#/////////////////////// INCUBATION REVIEW API ///////////////////////


class IncubationReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, idea_id):
        idea = get_object_or_404(Idea, id=idea_id)
        reviews = EvaluationService.get_incubation_reviews(request.user, idea)
        serializer = IncubationReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, idea_id):
        idea = get_object_or_404(Idea, id=idea_id)
        review = EvaluationService.create_incubation_review(
            user=request.user,
            idea=idea,
            data=request.data
        )
        serializer = IncubationReviewSerializer(review)
        return Response(serializer.data)
    
#///////////////////////////// NEXT UPCOMING SESSION API ////////////////////////

class NextUpcomingSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = EvaluationService.get_next_session(request.user)

        if not data:
            return Response({
                "message": "لا توجد جلسات قادمة"
            })

        return Response(data)
    



# ////////////////////////////////// MY EVALUATION DETAIL //////////////////////////////////
# 
# #UNUSED

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
#unused

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
#unused

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
    