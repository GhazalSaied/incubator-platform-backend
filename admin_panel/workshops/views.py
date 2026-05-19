from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import CanManageWorkshops
from .services import (
    WorkshopManagementService,
    WorkshopQueryService
)

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\كل الورشات \\\\\\\\\\\\\\\\\\\\\\\\\
class WorkshopListAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManageWorkshops]
    def get(self, request):

        data = WorkshopQueryService.list_workshops()

        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل الورشة///////////////////////
class WorkshopDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManageWorkshops]

    def get(self, request, workshop_id):

        data = WorkshopQueryService.get_workshop_details(
            workshop_id=workshop_id
        )

        return Response(data)
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول ورشة\\\\\\\\\\\\\\\\\\\\\
class ApproveWorkshopAPIView(APIView):

    permission_classes = [IsAuthenticated, CanManageWorkshops]

    def post(self, request, workshop_id):

        WorkshopManagementService.approve_workshop(
            workshop_id=workshop_id
        )

        return Response({
            "message": "تم قبول الورشة بنجاح"
        })
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\رفض ورشة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class RejectWorkshopAPIView(APIView):

    permission_classes = [IsAuthenticated, CanManageWorkshops]

    def post(self, request, workshop_id):

        rejection_reason = request.data.get(
            "rejection_reason"
        )

        WorkshopManagementService.reject_workshop(
            workshop_id=workshop_id,
            rejection_reason=rejection_reason
        )

        return Response({
            "message": "تم رفض الورشة"
        })