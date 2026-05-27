from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import CanManageBootcamp, CanManageCandidateBootcamp

from .services import (
    AbsenceQueryService,
    process_absence_decision
)
from bootcamp.serializers import (
    AbsenceRequestSerializer,
    AbsenceDecisionSerializer
)

#\\\\\\\AbsenceRequestsList\\\\\

class AbsenceRequestsListView(APIView):
    
    parser_classes = [IsAuthenticated, CanManageBootcamp]
    def get(self, request):
        query = request.query_params.get("search")

        queryset = AbsenceQueryService.search(query=query)
        serializer = AbsenceRequestSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
#\\\\AbsenceDecision\\\\\\\\\\\\\
class AbsenceDecisionView(APIView):
    permission_classes = [IsAuthenticated, CanManageCandidateBootcamp]
    def post(self, request, pk):
        serializer = AbsenceDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        absence = process_absence_decision(
            request_id=pk,  
            decision=serializer.validated_data["decision"],
            actor=request.user
        )

        return Response({
            "status": "success",
            "absence_id": absence.id,
            "absence_status": absence.status
        }, status=status.HTTP_200_OK)