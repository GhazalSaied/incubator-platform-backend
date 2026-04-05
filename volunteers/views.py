from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from messaging.models import Conversation
from django.shortcuts import get_object_or_404

from notifications.models import Notification
from messaging.models import Conversation

from .models import (
    VolunteerProfile,
    VolunteerAvailability,
    ConsultationRequest, 
    VolunteerJoinRequest,
      
      )
from .serializers import (
    VolunteerProfileSerializer,
    VolunteerAvailabilitySerializer,
    VolunteerAvailabilityCreateUpdateSerializer,
    VolunteerJoinRequestSerializer,
    CreateConsultationRequestSerializer,
)
from core.permissions import IsVolunteer
from ideas.models import TeamMember
from notifications.services.notification_service import NotificationService



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
            volunteer=request.user.volunteer_profile
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
            volunteer=request.user.volunteer_profile
        ).delete()

        serializer = VolunteerAvailabilitySerializer(
            data=request.data,
            many=True
        )
        serializer.is_valid(raise_exception=True)

        for item in serializer.validated_data:
            VolunteerAvailability.objects.create(
                volunteer=request.user.volunteer_profile,
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

#///////////////////////// Consultation REQUEST VIEW ///////////////////////////////////

class MyConsultationRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVolunteer]

    def get(self, request):
        profile = request.user.volunteer_profile

        request_type = request.query_params.get("type")

        requests = ConsultationRequest.objects.filter(
            volunteer=profile
        )

        if request_type:
            requests = requests.filter(request_type=request_type)

        requests = requests.order_by("-created_at")

        serializer = ConsultationRequestSerializer(requests, many=True)
        return Response(serializer.data)


#///////////////////////// [ACCEPT/REJECT] Consultation ///////////////////////////////////

class ConsultationRequestDecisionAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVolunteer]

    def post(self, request, request_id):

        action = request.data.get("action")

        if action not in ["accept", "reject"]:
            return Response({"detail": "إجراء غير صالح"}, status=400)

        from volunteers.services.volunteer_service import VolunteerService

        try:
            consultation = VolunteerService.handle_consultation_decision(
                user=request.user,
                request_id=request_id,
                action=action
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        return Response(ConsultationRequestSerializer(consultation).data)
    

#/////////////////////////////// VOLUNTEER DASHBOARD VIEW //////////////////////////////////////////////

class VolunteerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVolunteer]

    def get(self, request):

        from volunteers.services.volunteer_service import VolunteerService

        try:
            data = VolunteerService.get_dashboard(request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response({
            "profile": VolunteerProfileSerializer(data["profile"]).data,
            "availability": VolunteerAvailabilitySerializer(
                data["availability"], many=True
            ).data,
            "consultations": data["consultations"]
        })


#//////////////////////////////////  VOLUNTEER REQUESTS  /////////////////////////////////////////

class VolunteerRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVolunteer]

    def get(self, request):
        profile = request.user.volunteer_profile

        request_type = request.query_params.get("type")

        consultations = profile.consultation_requests.all()
        joins = profile.join_requests.all()

        if request_type == "consultation":
            return Response({
                "consultations": ConsultationRequestSerializer(consultations, many=True).data
            })

        elif request_type == "join":
            return Response({
                "join_requests": VolunteerJoinRequestSerializer(joins, many=True).data
            })

        return Response({
            "consultations": ConsultationRequestSerializer(consultations, many=True).data,
            "join_requests": VolunteerJoinRequestSerializer(joins, many=True).data,
        })
    
    
#//////////////////////////// CREATE CONSULTATION REQUEST /////////////////////////////////////////

class CreateConsultationRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateConsultationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        consultation = serializer.save(
            requester=request.user
        )

        return Response(
            ConsultationRequestSerializer(consultation).data,
            status=status.HTTP_201_CREATED
        )

#//////////////////////////////////// CONSULTATION REQUEST DETAILS ///////////////////////////////////

class ConsultationRequestDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVolunteer]

    def get(self, request, request_id):
        try:
            consultation = get_object_or_404(
                ConsultationRequest,
                id=request_id,
                 volunteer=request.user.volunteer_profile
            )
        except ConsultationRequest.DoesNotExist:
            return Response(
                {"detail": "غير موجود"},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {
            "id": consultation.id,
            "idea_title": consultation.idea.title if consultation.idea else None,
            "idea_description": consultation.idea.description,
            "request_type": consultation.request_type,
            "description": consultation.description,
            "status": consultation.status,
            "requester_email": consultation.requester.email,
        }

        return Response(data)

#//////////////////////////////////// Assigned Projects APIView  ////////////////////////////////////////

class AssignedProjectsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVolunteer]

    def get(self, request):
        profile = request.user.volunteer_profile

        #  الاستشارات المقبولة
        consultations = ConsultationRequest.objects.filter(
            volunteer=profile,
            status=ConsultationRequest.ACCEPTED,
            request_type=ConsultationRequest.CONSULTATION
        )

        consultations_data = [
            {
                "idea_id": c.idea.id,
                "idea_title": c.idea.title,
                "description": c.description,
            }
            for c in consultations
        ]

        #  المتابعة (حالياً نفس الاستشارات)
        ongoing_data = consultations_data

        #  المشاريع المنضم لها
        joined = TeamMember.objects.filter(user=request.user)

        joined_data = [
            {
                "idea_id": j.idea.id,
                "idea_title": j.idea.title,
                "description": j.idea.description,
            }
            for j in joined
        ]

        return Response({
            "consultations": consultations_data,
            "ongoing": ongoing_data,
            "joined_projects": joined_data
        })