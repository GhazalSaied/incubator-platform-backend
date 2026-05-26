import logging

from notifications.models import Notification
from notifications.serializers import NotificationSerializer

from messaging.domain.services.realtime_service import (
    RealtimeService,
)

logger = logging.getLogger(__name__)


class NotificationRealtimeService:

    # =====================================
    # PUBLIC
    # =====================================

    @classmethod
    def broadcast_created(
        cls,
        *,
        notification: Notification,
    ):

        try:

            payload = cls._build_created_payload(
                notification
            )

            RealtimeService.broadcast_notification(
                user_id=notification.user_id,
                payload=payload,
            )

        except Exception:

            logger.exception(
                "Failed to broadcast notification created event",
                extra={
                    "notification_id": notification.id,
                    "user_id": notification.user_id,
                }
            )

    # -------------------------------------

    @classmethod
    def broadcast_read(
        cls,
        *,
        notification: Notification,
    ):

        try:

            payload = cls._build_read_payload(
                notification
            )

            RealtimeService.broadcast_notification(
                user_id=notification.user_id,
                payload=payload,
            )

        except Exception:

            logger.exception(
                "Failed to broadcast notification read event",
                extra={
                    "notification_id": notification.id,
                    "user_id": notification.user_id,
                }
            )

    # -------------------------------------

    @classmethod
    def broadcast_all_read(
        cls,
        *,
        user,
    ):

        try:

            payload = cls._build_all_read_payload(
                user
            )

            RealtimeService.broadcast_notification(
                user_id=user.id,
                payload=payload,
            )

        except Exception:

            logger.exception(
                "Failed to broadcast all notifications read event",
                extra={
                    "user_id": user.id,
                }
            )

    # =====================================
    # PAYLOAD BUILDERS
    # =====================================

    @classmethod
    def _build_created_payload(
        cls,
        notification,
    ):

        unread_count = cls._get_unread_count(
            notification.user_id
        )

        return {
            "event": "NOTIFICATION_CREATED",
            "notification": NotificationSerializer(
                notification
            ).data,
            "unread_count": unread_count,
            "has_unread_notifications": unread_count > 0,
        }

    # -------------------------------------

    @classmethod
    def _build_read_payload(
        cls,
        notification,
    ):

        unread_count = cls._get_unread_count(
            notification.user_id
        )

        return {
            "event": "NOTIFICATION_READ",
            "notification_id": notification.id,
            "unread_count": unread_count,
            "has_unread_notifications": unread_count > 0,
        }

    # -------------------------------------

    @classmethod
    def _build_all_read_payload(
        cls,
        user,
    ):

        return {
            "event": "NOTIFICATIONS_ALL_READ",
            "unread_count": 0,
            "has_unread_notifications": False,
        }

    # =====================================
    # HELPERS
    # =====================================

    @staticmethod
    def _get_unread_count(
        user_id,
    ):

        return Notification.objects.filter(
            user_id=user_id,
            is_read=False,
        ).count()