from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import IdeaOwnerProfileSerializer


#///////////////////////// IDEA OWNER PROFILE /////////////////////////////

class IdeaOwnerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = IdeaOwnerProfileSerializer(
            instance={},
            context={"request": request}
        )
        return Response(serializer.data)

