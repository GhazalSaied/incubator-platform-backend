from django.contrib.auth import get_user_model
from notifications.models import Notification
from django.shortcuts import get_object_or_404
from notifications.services.template_service import TEMPLATES
from notifications.services.preference_service import PreferenceService
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()


class NotificationService:

    # /////////////////////////// SEND NOTIFICATION //////////////////

    @staticmethod
    def send(
        user,
        *,
        event_name=None,
        title=None,
        message=None,
        obj=None,
        actor=None,
        extra=None,
        notification_type=Notification.INFO,
        action_type=None,
        action_url=None,
        related_object=None,
        target_role=None,
    ):

        #  CHECK USER PREFERENCES
        if event_name and target_role:
            is_allowed = PreferenceService.is_enabled(
                user=user,
                event_name=event_name,
                role=target_role
            )
            if not is_allowed:
                return None

        #  TEMPLATE MODE
        if event_name:
            template = TEMPLATES.get(event_name)

            if not template:
                raise Exception(f"No template for event: {event_name}")

            title = template["title"]

            if obj and actor:
                message = template["message"](obj, actor)
            elif obj:
                message = template["message"](obj)
            elif actor:
                message = template["message"](actor)
            else:
                message = template["message"](extra)

        #  VALIDATION
        if not title or not message:
            raise Exception("Notification must have title and message")

        #  RELATED OBJECT
        related_object_id = None
        related_object_type = None

        if related_object:
            related_object_id = related_object.id
            related_object_type = related_object.__class__.__name__

        #  DEFAULT action_url 
        if action_url is None:
            action_url = ""

        # CREATE
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=notification_type,
            action_type=action_type,
            action_url=action_url,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            target_role=target_role
        )

        #  REALTIME DISPATCH
        NotificationService._dispatch(notification)

        return notification

    # /////////////////////////// REALTIME //////////////////

    @staticmethod
    def _dispatch(notification):

        try:
            channel_layer = get_channel_layer()

            if not channel_layer:
                return

            group_name = f"user_{notification.user.id}"

            data = {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "action_url": notification.action_url,
                "created_at": str(notification.created_at),
            }

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "data": data
                }
            )

        except Exception:
            # ما بدنا نكسر النظام لو realtime فشل
            pass

    # --------------------------------------

    @staticmethod
    def bulk_send(users, **kwargs):
        Notification.objects.bulk_create([
            Notification(user=user, **kwargs)
            for user in users
        ])

    # --------------------------------------

    @staticmethod
    def get_user_notifications(user):
        return Notification.objects.filter(user=user).only(
            "id", "title", "message", "type", "is_read", "created_at"
        ).order_by("-created_at")

    # --------------------------------------

    @staticmethod
    def mark_as_read(user, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=user
        )

        NotificationService._mark_single_as_read(notification)
        return notification

    # --------------------------------------

    @staticmethod
    def mark_all_as_read(user):
        Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True)

    # --------------------------------------

    @staticmethod
    def get_unread_data(user):
        unread_count = Notification.objects.filter(
            user=user,
            is_read=False
        ).count()

        return {
            "count": unread_count,
            "has_unread": unread_count > 0
        }

    # --------------------------------------

    @staticmethod
    def _mark_single_as_read(notification: Notification):
        notification.is_read = True
        notification.save(update_fields=["is_read"])