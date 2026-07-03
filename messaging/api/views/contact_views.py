from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from messaging.api.serializers.contact_serializers import (
    ContactUsSerializer,
)

from messaging.domain.services.contact_service import (
    ContactService,
)


class ContactUsAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = ContactUsSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        conversation = (
            ContactService.send_contact_message(
                sender=request.user,
                inquiry_type=serializer.validated_data["type"],
                message=serializer.validated_data["message"],
            )
        )

        return Response({
            "detail": "تم إرسال رسالتك بنجاح.",
            "conversation_id": conversation.id,
        })