from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import IdeaOwnerIncubationSerializer


#///////////////////////// IDEA OWNER PROFILE /////////////////////////////

class IdeaOwnerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "name": getattr(user, "full_name", user.email),
            "email": user.email,
            "avatar": user.avatar.url if hasattr(user, "avatar") and user.avatar else None
        })

#//////////////////////// CONTACT ADMIN ////////////////////////////

class ContactAdminAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get("message")
        inquiry_type = request.data.get("type")

        return Response({
            "detail": "تم إرسال رسالتك للإدارة"
        })