from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer
from ideas.models import TeamMember
from notifications.services.notification_service import NotificationService


#//////////////// GET ALL NOTIFICATIONS /////////////////////

class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.query_params.get("role")

        try:
            notifications = NotificationService.get_user_notifications(
                user=request.user,
                role=role
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(serializer.data)

#///////////////////////////////// MARK AS READ /////////////////////////////

class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):

        try:
            NotificationService.mark_as_read(
                request.user,
                notification_id
            )

        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"detail": "Notification marked as read"},
            status=status.HTTP_200_OK
        )
    
#////////////////////////////// MAKE ALL NOTIFICATION AS READ /////////////////////////

class MarkAllNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        updated_count = NotificationService.mark_all_as_read(
            request.user
        )

        return Response({
            "detail": "Notifications marked as read",
            "updated_count": updated_count
        })


    
#///////////////////////////////// NOTIFIACTION BADGE (UNREAD NOTIFICATION )/////////////////////

class NotificationBadgeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = NotificationService.get_unread_data(
            request.user
        )

        return Response(data)
