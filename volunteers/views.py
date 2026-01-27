from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import VolunteerProfile, VolunteerAvailability
from .serializers import (
    VolunteerProfileSerializer,
    VolunteerAvailabilitySerializer,
    VolunteerAvailabilityCreateUpdateSerializer
)
from core.permissions import IsVolunteer


#/////////////////////////// VOLUNTEER APPLY ///////////////////////

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


#/////////////////////////// VOLUNTEER PROFILE ///////////////////////

class VolunteerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVolunteer]

    def get(self, request):
        return Response(
            VolunteerProfileSerializer(
                request.user.volunteer_profile
            ).data
        )


#/////////////////////////// VOLUNTEER AVAILABILITY ///////////////////////

class VolunteerAvailabilityAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVolunteer]

    def get(self, request):
        availability = VolunteerAvailability.objects.filter(
            volunteer=request.user
        ).order_by("day")

        serializer = VolunteerAvailabilitySerializer(availability, many=True)
        return Response(serializer.data)

    def put(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"detail": "البيانات يجب أن تكون قائمة"},
                status=status.HTTP_400_BAD_REQUEST
            )

        VolunteerAvailability.objects.filter(
            volunteer=request.user
        ).delete()

        serializer = VolunteerAvailabilitySerializer(
            data=request.data,
            many=True
        )
        serializer.is_valid(raise_exception=True)

        for item in serializer.validated_data:
            VolunteerAvailability.objects.create(
                volunteer=request.user,
                **item
            )

        return Response(
            {"detail": "تم تحديث التوفر الأسبوعي بنجاح"},
            status=status.HTTP_200_OK
        )

#/////////////////////////// UPDATE VOLUNTEER PROFILE ///////////////////////

class VolunteerProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            profile = request.user.volunteer_profile
        except VolunteerProfile.DoesNotExist:
            return Response(
                {"detail": "أنت لست متطوعاً"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VolunteerProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            VolunteerProfileSerializer(profile).data,
            status=status.HTTP_200_OK
        )
    
#/////////////////////////// AVAILABLITY  CREATE ///////////////////////

class VolunteerAvailabilityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = request.user.volunteer_profile
        except VolunteerProfile.DoesNotExist:
            return Response(
                {"detail": "أنت لست متطوعاً"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VolunteerAvailabilityCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        availability = serializer.save(volunteer=profile)

        return Response(
            VolunteerAvailabilityCreateUpdateSerializer(availability).data,
            status=status.HTTP_201_CREATED
        )

#////////////////////////////// AVAILABLITY UPDATE //////////////////////////////

class VolunteerAvailabilityUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, availability_id):
        try:
            availability = VolunteerAvailability.objects.get(
                id=availability_id,
                volunteer=request.user.volunteer_profile
            )
        except (VolunteerAvailability.DoesNotExist, VolunteerProfile.DoesNotExist):
            return Response(
                {"detail": "غير مسموح"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VolunteerAvailabilityCreateUpdateSerializer(
            availability,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

#///////////////////////// AVAILABLITY DELETE ///////////////////////////


class VolunteerAvailabilityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, availability_id):
        try:
            availability = VolunteerAvailability.objects.get(
                id=availability_id,
                volunteer=request.user.volunteer_profile
            )
        except (VolunteerAvailability.DoesNotExist, VolunteerProfile.DoesNotExist):
            return Response(
                {"detail": "غير مسموح"},
                status=status.HTTP_404_NOT_FOUND
            )

        availability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
