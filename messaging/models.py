from django.db import models
from django.conf import settings
from common.models import BaseModel
from messaging.domain.constants.messaging_constants import ConversationType
User = settings.AUTH_USER_MODEL

#////////////////// CONVERSATION /////////////////////////////////


class Conversation(BaseModel):



    type = models.CharField(
    max_length=20,
    choices=ConversationType.CHOICES,
    default=ConversationType.PRIVATE,
    db_index=True,
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_conversations",
    )

    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    avatar = models.ImageField(
        upload_to="conversation_avatars/",
        null=True,
        blank=True,
    )

    last_message = models.ForeignKey(
        "Message",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-last_message_at", "-created_at"]
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["last_message_at"]),
        ]

    def __str__(self):
        return f"{self.type} Conversation #{self.id}"


#//////////////////////////// CONVERSATION PARTICIPANT /////////////////////////

class ConversationParticipant(BaseModel):

    conversation = models.ForeignKey(
        Conversation,
        related_name="participants",
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        User,
        related_name="conversation_participations",
        on_delete=models.CASCADE,
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
    )
    #TODO:
    # Consider indexing last_read_message later
    # if read receipt queries become heavy.
    last_read_message = models.ForeignKey(
        "Message",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    last_read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    unread_count = models.PositiveIntegerField(
        default=0,
    )

    is_muted = models.BooleanField(default=False)

    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = [
            ("conversation", "user"),
        ]
        indexes = [
            models.Index(fields=["user", "conversation"]),
            models.Index(fields=["conversation"]),
            models.Index(fields=["user", "unread_count"]),
        ]

    def __str__(self):
        return f"{self.user} in Conversation #{self.conversation_id}"
        
#///////////////////// MESSAGE ///////////////////////////////////////////

class Message(BaseModel):

    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",
        on_delete=models.CASCADE,
    )

    sender = models.ForeignKey(
        User,
        related_name="sent_messages",
        on_delete=models.CASCADE,
    )

    content = models.TextField()

    is_deleted = models.BooleanField(default=False)


    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
        ]

    def __str__(self):
        return f"Message #{self.id} by {self.sender}"
