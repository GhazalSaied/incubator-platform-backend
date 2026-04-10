from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from ideas.models import TeamMember


    
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

#//////////////////////////// NOTIFICATION FILTERING //////////////////////



class MyNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.query_params.get("role")
        user = request.user

        notifications = Notification.objects.filter(user=user)

        #  Role validation
        valid_roles = []

        if user.ideas.exists():
            valid_roles.append("IDEA_OWNER")

        if hasattr(user, "volunteer_profile"):
            valid_roles.append("VOLUNTEER")

        if TeamMember.objects.filter(user=user).exists():
            valid_roles.append("TEAM_MEMBER")

        #  apply filter only if valid
        if role and role in valid_roles:
            notifications = notifications.filter(target_role=role)

        notifications = notifications.order_by("-created_at")

        data = [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "role": n.target_role,
                "created_at": n.created_at,
                "action_url": n.action_url,
                "is_read": n.is_read,
            }
            for n in notifications
        ]

        return Response(data)
