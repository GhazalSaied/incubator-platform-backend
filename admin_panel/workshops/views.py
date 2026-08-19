from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import CanManageWorkshops
from .services import (
    WorkshopManagementService,
    WorkshopQueryService
)
from rest_framework.exceptions import ValidationError
from rest_framework import status

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\كل الورشات \\\\\\\\\\\\\\\\\\\\\\\\\
class WorkshopListAPIView(APIView):
    #permission_classes = [IsAuthenticated, CanManageWorkshops]
    def get(self, request):

        data = WorkshopQueryService.list_workshops()

        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل الورشة///////////////////////
class WorkshopDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManageWorkshops]

    def get(self, request, id):

        data = WorkshopQueryService.get_workshop_details(
            workshop_id=id,
            request=request
        )

        return Response(data)
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول ورشة\\\\\\\\\\\\\\\\\\\\\
class ApproveWorkshopAPIView(APIView):

    permission_classes = [IsAuthenticated, CanManageWorkshops]

    def post(self, request, workshop_id):

        try:
            WorkshopManagementService.approve_workshop(
                workshop_id=workshop_id
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "تم قبول الورشة بنجاح"},
            status=status.HTTP_200_OK
        )


class RejectWorkshopAPIView(APIView):

    permission_classes = [IsAuthenticated, CanManageWorkshops]

    def post(self, request, workshop_id):

        rejection_reason = request.data.get("rejection_reason")

        try:
            WorkshopManagementService.reject_workshop(
                workshop_id=workshop_id,
                rejection_reason=rejection_reason
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "تم رفض الورشة بنجاح"},
            status=status.HTTP_200_OK
        )