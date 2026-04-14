
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.management_service import VolunteerManagementService
from django.core.exceptions import ValidationError

from .services.query_service import VolunteerQueryService

#\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع المعلقة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class PendingVolunteersView(APIView):

    def get(self, request):

        data = VolunteerQueryService.get_pending_volunteers()

        return Response(data)
    
    
    
#\\\\\\\\\\\\\\\\\\\\\\تفاصيل طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.query_service import VolunteerQueryService


class VolunteerDetailsView(APIView):

    def get(self, request, volunteer_id):

        data = VolunteerQueryService.get_volunteer_details(
            volunteer_id=volunteer_id
        )

        if not data:
            return Response(
                {"error": "المتطوع غير موجود"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\قبول طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ApproveVolunteerView(APIView):

    def post(self, request, volunteer_id):

        try:
            VolunteerManagementService.approve_volunteer(
                volunteer_id=volunteer_id
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "تم قبول المتطوع بنجاح"})


# ----------------------------------------
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\رفض طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class RejectVolunteerView(APIView):

    def post(self, request, volunteer_id):

        try:
            VolunteerManagementService.reject_volunteer(
                volunteer_id=volunteer_id
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "تم رفض المتطوع"})