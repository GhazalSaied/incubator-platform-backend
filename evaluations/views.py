from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Evaluation
from .serializers import EvaluationSerializer
from ideas.models import Idea



#////////////////////////////////  CRAETE OR EDIT EVALUATION ////////////////////////


class EvaluationCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, idea_id):
        idea = Idea.objects.get(id=idea_id)

        evaluation, created = Evaluation.objects.get_or_create(
            evaluator=request.user,
            idea=idea,
            defaults={
                "score": request.data.get("score", 0),
                "notes": request.data.get("notes", "")
            }
        )

        if not created and evaluation.is_submitted:
            return Response(
                {"detail": "لا يمكن تعديل تقييم تم إرساله"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EvaluationSerializer(
            evaluation,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
#////////////////////// EVALUATION SUBMIT ////////////////////////////////////


class EvaluationSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, idea_id):
        evaluation = Evaluation.objects.get(
            evaluator=request.user,
            idea_id=idea_id
        )

        evaluation.is_submitted = True
        evaluation.save()

        return Response(
            {"detail": "تم إرسال التقييم بنجاح"},
            status=status.HTTP_200_OK
        )


#/////////////////////////// PREVIOUS EVALUATIONS //////////////////////////////


class MyEvaluationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, idea_id):
        evaluations = Evaluation.objects.filter(
            evaluator=request.user,
            idea_id=idea_id
        ).order_by("-created_at")

        serializer = EvaluationSerializer(evaluations, many=True)
        return Response(serializer.data)
