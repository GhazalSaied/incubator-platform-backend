from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import VolunteerProfile
from .serializers import VolunteerProfileSerializer



#/////////////////////////// VOLUNTREE REQUEST ///////////////////////


class VolunteerApplyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, "volunteer_profile"):
            return Response(
                {"detail": "لديك طلب تطوع سابق"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VolunteerProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = serializer.save(user=request.user)

        return Response(
            VolunteerProfileSerializer(profile).data,
            status=status.HTTP_201_CREATED
        )

#///////////////////////////////// VOLUNTREE PROFILE VIEW ////////////////////////

class VolunteerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.volunteer_profile
        except VolunteerProfile.DoesNotExist:
            return Response(
                {"detail": "أنت لست متطوعاً"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            VolunteerProfileSerializer(profile).data
        )
