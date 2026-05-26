
from django.urls import path

from messaging.api.views import (
    ConversationListAPIView,
    ConversationDetailAPIView,
    StartConversationAPIView,

    ConversationMessagesAPIView,
    SendMessageAPIView,
    MarkConversationAsReadAPIView,
    UnreadMessagesCountAPIView,
    GlobalUnreadMessagesCountAPIView,
)

urlpatterns = [

    # =====================================
    # Conversations
    # =====================================

    path(
        "conversations/",
        ConversationListAPIView.as_view(),
    ),

    path(
        "conversations/start/",
        StartConversationAPIView.as_view(),
    ),

    path(
        "conversations/<int:conversation_id>/",
        ConversationDetailAPIView.as_view(),
    ),

    # =====================================
    # Messages
    # =====================================

    path(
        "conversations/<int:conversation_id>/messages/",
        ConversationMessagesAPIView.as_view(),
    ),

    path(
        "conversations/<int:conversation_id>/messages/send/",
        SendMessageAPIView.as_view(),
    ),

    path(
        "conversations/<int:conversation_id>/read/",
        MarkConversationAsReadAPIView.as_view(),
    ),

    path(
        "conversations/<int:conversation_id>/unread-count/",
        UnreadMessagesCountAPIView.as_view(),
    ),

    path(
    "messages/unread-count/",
    GlobalUnreadMessagesCountAPIView.as_view(),
),
]

