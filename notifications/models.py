from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

#//////////////////////////////// NOTIFICATION MODEL //////////////////////////

class Notification(models.Model):

    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"

    TYPE_CHOICES = [
        (INFO, "Info"),
        (SUCCESS, "Success"),
        (WARNING, "Warning"),
    ]

    
    OPEN_CHAT = "OPEN_CHAT"
    VIEW_REQUEST = "VIEW_REQUEST"
    VIEW_IDEA = "VIEW_IDEA"

    ACTION_CHOICES = [
        (OPEN_CHAT, "Open Chat"),
        (VIEW_REQUEST, "View Request"),
        (VIEW_IDEA, "View Idea"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=INFO
    )

    
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)

    action_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user} - {self.title}"