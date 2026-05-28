from rest_framework.exceptions import APIException
from rest_framework import status

class MessagingException(Exception):
    default_message = "Messaging error occurred."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


# =========================
# Conversation Exceptions
# =========================

class ConversationNotFound(MessagingException):
    default_message = "Conversation not found."


class ConversationAccessDenied(APIException):

    status_code = status.HTTP_403_FORBIDDEN

    default_detail = "Access denied to this conversation."

    default_code = "conversation_access_denied"


class ConversationAlreadyExists(MessagingException):
    default_message = "Conversation already exists."


# =========================
# Message Exceptions
# =========================

class EmptyMessageContent(MessagingException):
    default_message = "Message content cannot be empty."


class MessageNotFound(MessagingException):
    default_message = "Message not found."