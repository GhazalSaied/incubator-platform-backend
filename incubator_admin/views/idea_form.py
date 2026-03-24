from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from incubator_admin.serializers.idea_form import IdeaFormSerializer
from core.permissions import IsAdminOrSecretary


class IdeaFormCreateView(APIView):
    permission_classes = [IsAdminOrSecretary]

    def post(self, request):
        serializer = IdeaFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
