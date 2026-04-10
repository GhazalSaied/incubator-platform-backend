from django.contrib.auth import get_user_model
from notifications.models import Notification
from django.shortcuts import get_object_or_404

User = get_user_model()


class NotificationService:

    # /////////////////////////// SEND NOTIFICATION //////////////////

    @staticmethod
    def send(
        user,
        title: str,
        message: str,
        *,
        notification_type=Notification.INFO,
        action_type=None,
        action_url=None,
        related_object=None,
    ):
        """
        Create a notification (DB حاليا)
        Future: ممكن نضيف email / push هون
        """

        related_object_id = None
        related_object_type = None

        if related_object:
            related_object_id = related_object.id
            related_object_type = related_object.__class__.__name__

        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=notification_type,
            action_type=action_type,
            action_url=action_url,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
        )

        #  Future Hook (لا تحذف!)
        NotificationService._dispatch(notification)

        return notification

    # --------------------------------------

    @staticmethod
    def bulk_send(users, **kwargs):
        """
        إرسال جماعي (مثلاً لكل المشاركين)
        """
        notifications = []

        Notification.objects.bulk_create([
            Notification(
                user=user,
                **kwargs
            )
            for user in users
        ])

        return notifications

    # --------------------------------------

    @staticmethod
    def get_user_notifications(user):
        """
        جميع إشعارات المستخدم
        """
        return Notification.objects.filter(user=user).only(
            "id", "title", "message", "type", "is_read", "created_at"
        ).order_by("-created_at")

    # --------------------------------------

    @staticmethod
    def mark_as_read(user, notification_id):
        """
        تعليم إشعار واحد كمقروء
        """

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
        """
        تعليم كل الإشعارات كمقروءة
        """
        Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True)

    # --------------------------------------

    @staticmethod
    def get_unread_data(user):
        """
        عدد الإشعارات غير المقروءة + هل يوجد
        """
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
        """
        internal helper (لا تستخدم خارج السيرفيس)
        """
        notification.is_read = True
        notification.save(update_fields=["is_read"])

    # --------------------------------------

    @staticmethod
    def _dispatch(notification: Notification):
        """
        نقطة التوسعة المستقبلية
        """
        # لاحقاً:
        # EmailChannel.send(notification)
        # PushChannel.send(notification)
        pass
    @staticmethod
    def send_from_template(
        *,
        user,
        template,
        context=None,
        action_type=None,
        action_url=None,
        related_object=None,
    ):
        message = template.message

        if context:
            message = message.format(**context)

        return NotificationService.send(
            user=user,
            title=template.title,
            message=message,
            notification_type=Notification.INFO,
            action_type=action_type,
            action_url=action_url or "",
            related_object=related_object,
        )