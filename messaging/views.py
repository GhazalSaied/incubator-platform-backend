from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from django.db.models import Max
from core.events import EventBus
from django.db import models


from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, ConversationListSerializer
from notifications.models import Notification
from .pagination import MessagePagination
from notifications.services.notification_service import NotificationService

from django.contrib.auth import get_user_model
User = get_user_model()



#///////////////////////// Display all conservations /////////////////////////////

class MyConversationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(
            participants=request.user
        ).distinct().order_by("-last_message_time")

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

        messages = conversation.messages.order_by("-last_message_time")

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

        content = request.data.get("content", "").strip()

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
                EventBus.emit(
                    "message_sent",
                    payload={
                        "message": message,
                        "conversation": conversation,
                        "sender": request.user,
                        "receiver": user,
                    },
                    actor=request.user,
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

        EventBus.emit(
            "message_read",
            payload={
                "conversation_id": conversation.id,
                "user": request.user,
            },
            actor=request.user
        )

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
    
#///////////////////////////////////// CONVERSATION LIST VIEW //////////////////////

class ConversationListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationListSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).annotate(
            last_message_time=Max("messages__created_at")
        ).order_by("-last_message_time")

    def get_serializer_context(self):
        return {"request": self.request}


#///////////////////////////////// CONVERSATION DETAIL VIEW //////////////////////////////////


class ConversationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return Response({"detail": "غير مسموح"}, status=404)

        messages = conversation.messages.order_by("created_at")

        paginator = MessagePagination()
        paginated = paginator.paginate_queryset(messages, request)

        serializer = MessageSerializer(paginated, many=True)

        return paginator.get_paginated_response(serializer.data)
    

#//////////////////// START CONVERSATION //////////////////////

class StartConversationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"detail": "user_id مطلوب"},
                status=400
            )

        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "المستخدم غير موجود"}, status=404)

        # check existing conversation
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).annotate(
            num_participants=models.Count('participants')
        ).filter(num_participants=2).first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)

        return Response({
            "conversation_id": conversation.id
        })