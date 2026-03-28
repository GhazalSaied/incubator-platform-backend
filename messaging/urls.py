from django.urls import path
from .views import (
    MyConversationsAPIView,
    ConversationDetailAPIView,
    SendMessageAPIView,
    MarkAsReadAPIView,
    UnreadMessagesCountAPIView,
)

urlpatterns = [
    path("", MyConversationsAPIView.as_view()),
    path("<int:conversation_id>/", ConversationDetailAPIView.as_view()),
    path("<int:conversation_id>/send/", SendMessageAPIView.as_view()),
    path("<int:conversation_id>/read/", MarkAsReadAPIView.as_view()),
    path("unread-count/", UnreadMessagesCountAPIView.as_view()),
]