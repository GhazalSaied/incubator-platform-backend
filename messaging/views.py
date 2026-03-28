from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from notifications.models import Notification

#///////////////////////// Display all conservations /////////////////////////////

class MyConversationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(
            participants=request.user
        ).distinct().order_by("-created_at")

        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

#///////////////////////// Display Single conservation /////////////////////////////

class ConversationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "غير مسموح"},
                status=status.HTTP_404_NOT_FOUND
            )

        messages = conversation.messages.order_by("created_at")

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
#///////////////////////// Sending messages  /////////////////////////////

class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "غير مسموح"},
                status=status.HTTP_404_NOT_FOUND
            )

        content = request.data.get("content")

        if not content:
            return Response(
                {"detail": "الرسالة فارغة"},
                status=status.HTTP_400_BAD_REQUEST
            )

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )

        #  إرسال إشعارات لباقي المشاركين
        for user in conversation.participants.all():
            if user != request.user:
                Notification.objects.create(
                    user=user,
                    title="رسالة جديدة",
                    message=f"لديك رسالة جديدة من {request.user.full_name}",
                    type="INFO",
                    related_object_id=conversation.id,
                    related_object_type="conversation",
                    action_url=f"/chat/{conversation.id}"
                )

        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
#///////////////////////// Mark As Read View /////////////////////////////

class MarkAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return Response({"detail": "غير مسموح"}, status=404)

        conversation.messages.filter(
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)

        return Response({"detail": "تم القراءة"})
    
#/////////////////////////////// UNREAD MESSAGES COUNT ///////////////////////////

class UnreadMessagesCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()

        return Response({"unread_messages": count})