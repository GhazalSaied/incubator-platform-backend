from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ChatSession, ChatMessage
from .serializers import SendMessageSerializer
from .services.gemini_service import GeminiService
from django.http import StreamingHttpResponse
import json

class ChatStreamAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data.get("session_id")
        consultation_field = serializer.validated_data.get("consultation_field")
        user_message = serializer.validated_data["message"]

        if session_id:

           session = ChatSession.objects.get(
        id=session_id,
        user=request.user
    )

        else:

           session = ChatSession.objects.create(
        user=request.user,
        title=user_message[:50],
        consultation_field=consultation_field
    )

        ChatMessage.objects.create(
            session=session,
            sender="user",
            content=user_message
        )

        def event_stream():
            full_response = ""

            for chunk in GeminiService.stream_response(session, user_message):
                full_response += chunk

                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            ChatMessage.objects.create(
                session=session,
                sender="assistant",
                content=full_response
            )

            yield f"data: {json.dumps({'done': True, 'session_id': session.id})}\n\n"

        return StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream"
        )
        
class ChatSessionListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        sessions = ChatSession.objects.filter(user=request.user)

        data = [
            {
                "id": s.id,
                "title": s.title,
                "consultation_field": s.consultation_field,
                "updated_at": s.updated_at
            }
            for s in sessions
        ]

        return Response(data)
    
    
class ChatSessionDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):

        session = ChatSession.objects.get(
            id=session_id,
            user=request.user
        )

        messages = session.messages.all()

        data = {
            "session_id": session.id,
            "title": session.title,
            "messages": [
                {
                    "sender": m.sender,
                    "content": m.content,
                    "created_at": m.created_at
                }
                for m in messages
            ]
        }

        return Response(data)