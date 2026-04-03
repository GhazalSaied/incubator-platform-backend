from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationService:

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

        # 🔥 Future Hook (لا تحذف!)
        NotificationService._dispatch(notification)

        return notification

    # --------------------------------------

    @staticmethod
    def bulk_send(users, **kwargs):
        """
        إرسال جماعي (مثلاً لكل المشاركين)
        """
        notifications = []

        for user in users:
            notifications.append(
                NotificationService.send(user=user, **kwargs)
            )

        return notifications

    # --------------------------------------

    @staticmethod
    def mark_as_read(notification: Notification):
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