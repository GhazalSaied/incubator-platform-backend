from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ideas.models import Idea
from bootcamp.models import BootcampAttendance

class SessionAttendanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        attendance = BootcampAttendance.objects.filter(session_id=session_id)
        
        data = []
        for a in attendance:
            data.append({
                "idea": a.idea.title,
                "status": a.status
            })

        return Response(data)
    
    
    
    
class IdeaAttendanceStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, idea_id):
        total = BootcampAttendance.objects.filter(idea_id=idea_id).count()

        absent = BootcampAttendance.objects.filter(
            idea_id=idea_id,
            status='absent'
        ).count()

        percentage = (absent / total * 100) if total > 0 else 0

        return Response({
            "total_sessions": total,
            "absent_sessions": absent,
            "absence_percentage": percentage
        })
        
        
class BootcampParticipantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ideas = Idea.objects.all()

        result = []

        for idea in ideas:
            total = BootcampAttendance.objects.filter(idea=idea).count()
            absent = BootcampAttendance.objects.filter(
                idea=idea,
                status='absent'
            ).count()

            absence = (absent / total * 100) if total > 0 else 0
            commitment = 100 - absence

            result.append({
                "idea_id": idea.id,
                "idea_title": idea.title,
                "owner": idea.owner.full_name,
                "commitment_percentage": commitment,
                "bootcamp_status": idea.bootcamp_status
            })

        return Response(result)