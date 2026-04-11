from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.services.user_dashboard_service import UserDashboardService

class MyDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserDashboardService.build(request.user)
        return Response(data)