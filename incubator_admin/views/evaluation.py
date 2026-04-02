from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ideas.models import Idea
from incubator_admin.serializers.evaluation import IdeaEvaluationListSerializer
from core.permissions import IsAdminOrSecretary


class IdeasForEvaluationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        # 🔥 فلترة أساسية: فقط المقبولة من المعسكر
        ideas = Idea.objects.filter(bootcamp_status="accepted")

        # 🔥 فلترة حسب القطاع (اختياري)
        sector = request.query_params.get("sector")

        if sector:
            ideas = ideas.filter(sector=sector)

        serializer = IdeaEvaluationListSerializer(ideas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)