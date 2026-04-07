from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import IsAdminOrSecretary

from .services import (
    get_absence_requests,
    process_absence_decision
)
from bootcamp.serializers import (
    AbsenceRequestSerializer,
    AbsenceDecisionSerializer
)

#\\\\\\\AbsenceRequestsList\\\\\

class AbsenceRequestsListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):
        queryset = get_absence_requests()
        serializer = AbsenceRequestSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
#\\\\AbsenceDecision\\\\\\\\\\\\\
class AbsenceDecisionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request):
        serializer = AbsenceDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        process_absence_decision(
            serializer.validated_data["request_id"],
            serializer.validated_data["decision"]
        )

        return Response({"detail": "تم اتخاذ القرار"}, status=status.HTTP_200_OK)