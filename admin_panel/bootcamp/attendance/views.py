from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from bootcamp.serializers import (
    SessionAttendanceSerializer,
    AttendanceStatsSerializer,
    BootcampParticipantSerializer
)

from admin_panel.bootcamp.attendance.services import (
    get_session_attendance,
    get_idea_stats,
    BootcampDecisionQueryService
)


#\\\\session attendance\\\\\\
class SessionAttendanceListView(APIView):
    
    def get(self, request, session_id):
        queryset = get_session_attendance(session_id)
        serializer = SessionAttendanceSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
#\\\\\\\\idea stats\\\\\\\\\\\
class IdeaAttendanceStatsView(APIView):
    

    def get(self, request, idea_id):
        data = get_idea_stats(idea_id)
        return Response(data)
    
#\\\\\\\participants\\\\\

class BootcampDecisionListView(APIView):
    

    def get(self, request):
        search = request.query_params.get("search")

        data = BootcampDecisionQueryService.list_decisions(search=search)

        return Response(data)