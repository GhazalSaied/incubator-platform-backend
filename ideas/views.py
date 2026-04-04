from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import status
from django.utils.timezone import now

from core.permissions import CanSubmitIdea
from .models import Idea, Season , IdeaStatus
from .serializers import (
    IdeaFormSerializer,
    IdeaCreateUpdateSerializer,
    IdeaDetailSerializer,
    MyIdeaListSerializer,
    TeamRequestSerializer,
)
from notifications.models import Notification
from ideas.services.idea_validation import IdeaFormValidator
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases  import SeasonPhase
from bootcamp.serializers import BootcampSessionSerializer
from bootcamp.models import BootcampSession
from evaluations.models import IncubationReview
from evaluations.serializers import IncubationReviewSerializer
from volunteers.models import VolunteerProfile , ConsultationRequest
from notifications.services.notification_service import NotificationService
from ideas.services.idea_service import IdeaService


#///////////////////////////GET CUURENT IDEA FORM /////////////////////////////////

class CurrentIdeaFormAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        season = Season.objects.filter(is_open=True).first()
        if not season or not hasattr(season, 'form'):
            return Response(
                {"detail": "لا يوجد موسم مفتوح حالياً"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = IdeaFormSerializer(season.form)
        return Response(serializer.data)

#/////////////////////////// CREATE IDEA VIEW /////////////////////////////////

class IdeaCreateAPIView(APIView):
    permission_classes = [CanSubmitIdea]

    def post(self, request):

        serializer = IdeaCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            idea = IdeaService.submit_idea(
                user=request.user,
                data=serializer.validated_data
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            IdeaDetailSerializer(idea).data,
            status=status.HTTP_201_CREATED
        )


#///////////////////////// EDIT IDEA VIEW ///////////////////////////////////

class IdeaUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, idea_id):

        try:
            idea = Idea.objects.get(id=idea_id, owner=request.user)
        except Idea.DoesNotExist:
            return Response(
                {"detail": "الفكرة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = IdeaCreateUpdateSerializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        try:
            idea = IdeaService.update_idea(
                user=request.user,
                idea=idea,
                data=serializer.validated_data
            )
        except PermissionError as e:
            return Response({"detail": str(e)}, status=403)

        return Response(
            IdeaDetailSerializer(idea).data,
            status=status.HTTP_200_OK
        )


 #////////////////////////  WITHDRIDEAVIEW //////////////////////////////////////////

class WithdrawIdeaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, idea_id):

        try:
            idea = Idea.objects.get(id=idea_id, owner=request.user)
        except Idea.DoesNotExist:
            return Response(
                {"detail": "الفكرة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            IdeaService.withdraw_idea(
                user=request.user,
                idea=idea
            )
        except PermissionError as e:
            return Response({"detail": str(e)}, status=403)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(
            {"detail": "تم سحب الفكرة بنجاح"},
            status=status.HTTP_200_OK
        )


#///////////////////////////////// CURRENT SEASON PHASE ////////////////////////////////////////

class CurrentSeasonPhaseAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            return Response({
                "season": None,
                "phase": None
            })

        return Response({
            "season": {
                "id": season.id,
                "name": season.name
            },
            "phase": {
                "code": phase.phase,
                "start_date": phase.start_date,
                "end_date": phase.end_date
            }
        })

#//////////////////////////// MY IDEA VIEW (DISPLAY IDEA INFO TO THE USER ) /////////////////////////////////////

class MyIdeasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ideas = Idea.objects.filter(
            owner=request.user
        ).order_by("-created_at")

        serializer = MyIdeaListSerializer(ideas, many=True)
        return Response(serializer.data)

#////////////////////////////////// IDEA DASHBOARD VIEW  //////////////////////////

from ideas.services.idea_dashboard_service import IdeaDashboardService


class IdeaDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = IdeaDashboardService.build(request.user)

        if "detail" in data:
            return Response(data, status=404)

        return Response(data)
        

        
    
#//////////////////////////// INCUBATION PHASE //////////////////////////

class IncubationPhaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            data = IdeaService.get_incubation_data(request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(data)

#//////////////////////////////// EXHIBITION PHASE /////////////////////////////

class ExhibitionPhaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            data = IdeaService.get_exhibition_data(request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(data)


#//////////////////////////////// UPDATE EXHIBITION CARD  /////////////////////////////

class UpdateExhibitionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):

        try:
            IdeaService.update_exhibition(
                user=request.user,
                data=request.data,
                files=request.FILES
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        return Response({"detail": "تم تحديث بطاقة المشروع"})


#//////////////////////////// CREATE TEAM REQUEST VIEW ////////////////////////

class CreateTeamRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        from ideas.services.idea_service import IdeaService

        try:
            IdeaService.create_team_request(
                user=request.user,
                data=request.data
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        return Response({"detail": "طلبك قيد المراجعة"})
    

#/////////////////////////// SUGGESTED VOLUNTREES ///////////////////////////

class SuggestedVolunteersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = IdeaService.get_suggested_volunteers()
        return Response(data)

#///////////////////////////////// IDEA TEAM //////////////////////////

class IdeaTeamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        from ideas.services.idea_service import IdeaService

        try:
            idea = IdeaService.get_user_idea(request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        return Response({
            "current_team": [
                {
                    "email": m.user.email,
                    "role": m.role
                }
                for m in idea.team_members.all()
            ]
        })


#/////////////////////////// CONSULTANTS LIST ////////////////////////

class ConsultantsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = IdeaService.get_consultants()
        return Response(data)