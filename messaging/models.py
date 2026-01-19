from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

#////////////////// CONVERSATION /////////////////////////////////


class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

#///////////////////// MESSAGE ///////////////////////////////////////////

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
