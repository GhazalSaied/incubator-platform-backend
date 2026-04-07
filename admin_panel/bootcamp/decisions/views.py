from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsAdminOrSecretary, IsDirector

from bootcamp.serializers import (
    BootcampIdeaListSerializer,
    BootcampDecisionSerializer
)

from admin_panel.bootcamp.decisions.services import (
    get_bootcamp_ideas,
    process_bootcamp_decision
)

#\\\\\\\\\BootcampIdeasList\\\\\
class BootcampIdeasListView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]
    
    def get(self, request):
        search = request.query_params.get("search")

        data = get_bootcamp_ideas(search)

        serializer = BootcampIdeaListSerializer(data, many=True)
        return Response(serializer.data)
    
#\\\\\\\BootcampDecision\\\\\\\\\
class BootcampDecisionView(APIView):
    permission_classes = [IsAuthenticated, IsDirector]
    

    def post(self, request):
        serializer = BootcampDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idea = process_bootcamp_decision(
            serializer.validated_data["idea_id"],
            serializer.validated_data["decision"],
            serializer.validated_data["message"]
        )

        return Response({
            "idea_id": idea.id,
            "status": idea.status
        })
        
