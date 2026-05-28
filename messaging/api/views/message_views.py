
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from messaging.api.serializers.message_serializers import (
    MessageSerializer,
    SendMessageSerializer,
)

from messaging.api.pagination.message_pagination import (
    MessagePagination,
)

from messaging.domain.selectors.conversation_selectors import (
    get_user_conversation_by_id,
)

from messaging.domain.selectors.message_selectors import (
    get_conversation_messages,
    get_unread_messages_count,
    get_global_unread_messages_count,
)

from messaging.domain.services.message_service import (
    MessageService,
)

from messaging.domain.services.read_service import (
    ReadService,
)

from messaging.domain.exceptions.messaging_exceptions import (
    ConversationAccessDenied,
    EmptyMessageContent,
)

from messaging.api.throttles.message_throttles import SendMessageThrottle


# ==========================================
# Conversation Messages API
# ==========================================

class ConversationMessagesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        conversation = get_user_conversation_by_id(
            user=request.user,
            conversation_id=conversation_id,
        )

        if not conversation:
            raise ConversationAccessDenied()

        messages = get_conversation_messages(
            conversation
        )

        paginator = MessagePagination()

        paginated_messages = (
            paginator.paginate_queryset(
                messages,
                request,
            )
        )

        serializer = MessageSerializer(
            paginated_messages,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# ==========================================
# Send Message API
# ==========================================

class SendMessageAPIView(APIView):

    permission_classes = [IsAuthenticated]

    throttle_classes = [
        SendMessageThrottle
    ]

    def post(self, request, conversation_id):

        conversation = get_user_conversation_by_id(
            user=request.user,
            conversation_id=conversation_id,
        )

        if not conversation:
            raise ConversationAccessDenied()

        serializer = SendMessageSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            message = (
                MessageService.send_message(
                    conversation=conversation,
                    sender=request.user,
                    content=serializer.validated_data[
                        "content"
                    ],
                )
            )

        except EmptyMessageContent as e:

            return Response(
                {
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = MessageSerializer(
            message
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================
# Mark Conversation As Read API
# ==========================================

class MarkConversationAsReadAPIView(
    APIView
):

    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):

        conversation = get_user_conversation_by_id(
            user=request.user,
            conversation_id=conversation_id,
        )

        if not conversation:
            raise ConversationAccessDenied()

        ReadService.mark_conversation_as_read(
            conversation=conversation,
            user=request.user,
        )

        return Response(
            {
                "detail": "Conversation marked as read."
            }
        )


# ==========================================
# Unread Messages Count API
# ==========================================

class UnreadMessagesCountAPIView(
    APIView
):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        conversation = get_user_conversation_by_id(
            user=request.user,
            conversation_id=conversation_id,
        )

        if not conversation:
            raise ConversationAccessDenied()

        unread_count = (
            get_unread_messages_count(
                conversation=conversation,
                user=request.user,
            )
        )

        return Response(
            {
                "unread_count": unread_count
            }
        )

#=======================================
#GLOBAL Unread Messages Count (BADGE)
#=======================================

class GlobalUnreadMessagesCountAPIView(
    APIView
):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        unread_count = (
            get_global_unread_messages_count(
                request.user
            )
        )

        return Response({
            "unread_count": unread_count,
        })
