from django.contrib.auth import get_user_model
from notifications.models import Notification
from django.shortcuts import get_object_or_404
from notifications.services.template_service import TEMPLATES
from notifications.services.preference_service import PreferenceService
from notifications.services.notification_realtime_service import (
    NotificationRealtimeService,
)
from django.db.models import Q
from django.db import transaction

from accounts.constants import SystemRoles

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

            elif extra:
                message = template["message"](extra)

            elif actor:
                message = template["message"](actor)

            else:
                raise Exception("No notification payload provided")

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

        NotificationRealtimeService.broadcast_created(
            notification=notification
    )

    # --------------------------------------

    @staticmethod
    def bulk_send(users, **kwargs):
        Notification.objects.bulk_create([
            Notification(user=user, **kwargs)
            for user in users
        ])

    # --------------------------------------

    @staticmethod
    def get_user_notifications(user, role=None):
        queryset = Notification.objects.filter(user=user)

        # FILTER BY ROLE
        if role:

            # SECURITY VALIDATION
            if role not in user.role_codes:
                raise ValueError("Invalid role filter")

            queryset = queryset.filter(
                Q(target_role=role) |
                Q(target_role__isnull=True)
            )

        return queryset.only(
            "id",
            "message",
            "type",
            "is_read",
            "created_at",
            "target_role",
            "action_url",
        ).order_by("-created_at")

    # --------------------------------------
    # MARK SINGLE NOTIFICATION AS READ
    # --------------------------------------

    @staticmethod
    def mark_as_read(user, notification_id):
        notification = get_object_or_404(
            Notification.objects.only(
                "id",
                "user_id",
                "is_read"
            ),
            id=notification_id,
            user=user
        )

        NotificationService._mark_single_as_read(notification)
        NotificationRealtimeService.broadcast_read(
            notification=notification
        )

        return notification

    # --------------------------------------
    # MARK ALL NOTIFICATIONS AS READ
    # --------------------------------------

    @staticmethod
    @transaction.atomic
    def mark_all_as_read(user):
        updated_count = Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True)

        
        NotificationRealtimeService.broadcast_all_read(
            user=user
        )

        return updated_count

    # --------------------------------------
    # GET UNREAD BADGE DATA
    # --------------------------------------

    @staticmethod
    def get_unread_data(user):
        unread_count = Notification.objects.filter(
            user=user,
            is_read=False
        ).count()

        return {
            "unread_count": unread_count,
            "has_unread_notifications": unread_count > 0
        }

    # --------------------------------------
    # INTERNAL SINGLE READ HELPER
    # --------------------------------------

    @staticmethod
    def _mark_single_as_read(notification: Notification):

        if notification.is_read:
            return

        notification.is_read = True

        notification.save(
            update_fields=["is_read"]
        )