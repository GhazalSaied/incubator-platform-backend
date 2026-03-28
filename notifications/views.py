from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer

#////////////////////////// GET MY NOTIFICATIONS //////////////////////

class MyNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
#///////////////////////////////// MARK AS READ /////////////////////////////

class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
        except Notification.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        notification.is_read = True
        notification.save()

        return Response({"detail": "Marked as read"})
    
#////////////////////////////// MAKE ALL NOTIFICATION AS READ /////////////////////////

class MarkAllNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({"detail": "All marked as read"})

#////////////////////////////// UNREAD NOTIFICATION COUNT /////////////////////

class UnreadNotificationsCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({"unread_notifications": count})
    
#///////////////////////////////// NOTIFIACTION BADGE /////////////////////

class NotificationBadgeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({
            "has_unread": unread_count > 0,
            "count": unread_count
        })

#////////////////////////////// 

