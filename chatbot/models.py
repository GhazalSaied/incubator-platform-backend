from django.conf import settings
from django.db import models
from volunteers.models import PrimarySkillChoices

class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )

    title = models.CharField(
        max_length=255,
        blank=True
    )
    consultation_field = models.CharField(
    max_length=50,
    choices=PrimarySkillChoices.choices,blank=True
)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.email} - {self.title or 'New Chat'}"


class ChatMessage(models.Model):

    class SenderType(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.CharField(
        max_length=20,
        choices=SenderType.choices
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender} - {self.created_at}"