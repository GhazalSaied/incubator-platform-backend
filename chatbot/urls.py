from django.urls import path

from .views import ChatStreamAPIView,ChatSessionListAPIView,ChatSessionDetailAPIView

urlpatterns = [
    path(
        "chat/",
        ChatStreamAPIView.as_view(),
        name="chat"
    ),
    path(
        "sessions/",
        ChatSessionListAPIView.as_view(),
        name="chat-session-list"
    ),
    path(
        "sessions/<int:session_id>/",
        ChatSessionDetailAPIView.as_view(),
        name="chat-session-detail"
    )
]