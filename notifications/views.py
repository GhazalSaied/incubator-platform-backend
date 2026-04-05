from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer

#////////////////////////// GET MY NOTIFICATIONS //////////////////////

class MyNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        from notifications.services.notification_service import NotificationService

        notifications = NotificationService.get_user_notifications(request.user)

        return Response(
            NotificationSerializer(notifications, many=True).data
        )
    
#///////////////////////////////// MARK AS READ /////////////////////////////

class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):

        from notifications.services.notification_service import NotificationService

        try:
            NotificationService.mark_as_read(request.user, notification_id)
        except Notification.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        return Response({"detail": "Marked as read"})
    
#////////////////////////////// MAKE ALL NOTIFICATION AS READ /////////////////////////

class MarkAllNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request ):

        from notifications.services.notification_service import NotificationService

        NotificationService.mark_all_as_read(request.user)

        return Response({"detail": "All marked as read"})


    
#///////////////////////////////// NOTIFIACTION BADGE (UNREAD NOTIFICATION )/////////////////////

class NotificationBadgeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        from notifications.services.notification_service import NotificationService

        data = NotificationService.get_unread_data(request.user)

        return Response(data)


