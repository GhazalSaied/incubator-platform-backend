
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from django.contrib.auth import get_user_model

from messaging.api.serializers.conversation_serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
)

from messaging.api.serializers.message_serializers import (
    StartConversationSerializer,
)

from messaging.domain.selectors.conversation_selectors import (
    get_user_conversations,
    get_user_conversation_by_id,
)

from messaging.domain.services.conversation_service import (
    ConversationService,
)

from messaging.domain.exceptions.messaging_exceptions import (
    ConversationAccessDenied,
)

User = get_user_model()


# ==========================================
# Conversation List API
# ==========================================

class ConversationListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        search = request.query_params.get("search")

        conversations = get_user_conversations(
            request.user,
            search=search,
        )

        serializer = ConversationListSerializer(
            conversations,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


# ==========================================
# Conversation Detail API
# ==========================================

class ConversationDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        conversation = get_user_conversation_by_id(
            user=request.user,
            conversation_id=conversation_id,
        )

        if not conversation:
            raise PermissionDenied("Access denied.")

        serializer = ConversationDetailSerializer(
            conversation,
            context={"request": request},
        )

        return Response(serializer.data)


# ==========================================
# Start Conversation API
# ==========================================

class StartConversationAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = StartConversationSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user_id = serializer.validated_data[
            "user_id"
        ]

        try:
            target_user = User.objects.get(
                id=user_id
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        conversation = (
            ConversationService
            .start_private_conversation(
                creator=request.user,
                target_user=target_user,
            )
        )

        return Response(
            {
                "conversation_id": conversation.id
            },
            status=status.HTTP_200_OK,
        )

