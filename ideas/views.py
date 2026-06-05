from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import status
from django.utils.timezone import now
from core.events import EventBus

from .models import Idea, Season , IdeaStatus
from .serializers import (
    IdeaFormSerializer,
    IdeaDetailSerializer,
    MyIdeaListSerializer,
    TeamRequestSerializer,
    ExhibitionSubmissionCreateSerializer,
    ExhibitionFormDetailsSerializer,
    ExhibitionSubmissionCreateSerializer,
    PublicExhibitionListSerializer,
    PublicExhibitionDetailsSerializer,
    SubmissionFormSerializer,
    SaveStepSerializer,
    ProjectDetailsSerializer,
    
)
from notifications.models import Notification
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases  import SeasonPhase
from bootcamp.serializers import BootcampSessionsTableSerializer
from bootcamp.models import BootcampSession
from evaluations.models import IncubationReview
from evaluations.serializers import IncubationReviewSerializer
from volunteers.models import VolunteerProfile , ConsultationRequest
from notifications.services.notification_service import NotificationService
from ideas.services.idea_service import IdeaService
from ideas.services.idea_dashboard_service import IdeaDashboardService
from ideas.services.exhibition_service import (
    ExhibitionService,
)
from ideas.services.exhibition_public_service import ExhibitionPublicService
from ideas.services.idea_permissions import CanSubmitIdea
from core.permissions import (CanRequestTeamCompletion,
                              CanViewTeamCandidates
                            )

from ideas.services.idea_dashboard_service import IdeaDashboardService
from django.shortcuts import get_object_or_404
                              



#///////////////////////////GET CUURENT IDEA FORM /////////////////////////////////
#UNUSED
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


#/////////////////////////////// GET SUBMISSION FORM /////////////////////////// 

class SubmissionFormAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, season_id):

        season = get_object_or_404(Season, id=season_id)

        data = IdeaService.get_submission_form(
            user=request.user,
            season=season
        )

        serializer = SubmissionFormSerializer(instance=data)

        return Response(serializer.data)


#////////////////////////////// SAVE STEP ///////////////////////////////

class SaveStepAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, season_id):

        season = get_object_or_404(Season, id=season_id)

        serializer = SaveStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        IdeaService.save_step(
            user=request.user,
            season=season,
            step_order=serializer.validated_data["step"],
            payload=serializer.validated_data["data"]
        )

        return Response({
            "message": "تم حفظ الخطوة بنجاح"
        })


#////////////////////////// SUBMIT IDEA ///////////////////////////////

class SubmitIdeaAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, season_id):

        season = get_object_or_404(Season, id=season_id)

        idea = IdeaService.submit_idea(
            user=request.user,
            season=season
        )

        return Response({
            "message": "تم إرسال الفكرة بنجاح",
            "idea_id": idea.id,
            "status": idea.status,
        })


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



#////////////////////////////////// IDEA DASHBOARD VIEW  //////////////////////////

class IdeaDashboardAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        dashboard = (
            IdeaDashboardService
            .get_user_dashboard(
                request.user
            )
        )

        return Response(
            dashboard,
            status=status.HTTP_200_OK
        )
    

#//////////////////////////////// EXHIBITION DASHBOARD /////////////////////////////

class ExhibitionDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            dashboard = (
                ExhibitionService.get_exhibition_dashboard(
                    user=request.user
                )
            )
        except ValueError as e:
            return Response(
                {
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        form_serializer = ExhibitionFormDetailsSerializer(
            dashboard["form"]
        )

        form_data = None

        if dashboard["is_owner"]:
            form_data = ExhibitionFormDetailsSerializer(
                dashboard["form"]
            ).data

        submission_data = (
            dashboard["submission"].data
            if dashboard["submission"] 
            else None
        )

        return Response(
            {
                "phase": "EXHIBITION",
                "exhibition_date": dashboard["idea"].season.exhibition_datetime,
                "is_owner": dashboard["is_owner"],
                "can_edit": (
                    dashboard["is_owner"]
                    and dashboard["submission"] is None
                ),
                "form": form_data,
                "submitted_data": submission_data,
            },
            status=status.HTTP_200_OK
        )


#/////////////////////// EXHIBITION SUBMISSION CREATE /////////////////////////

class CreateExhibitionSubmissionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            idea, _ = (
                ExhibitionService.get_user_exhibition_idea(
                    request.user
                )
            )
        except ValueError as e:
            return Response(
                {
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ExhibitionSubmissionCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "idea": idea,
            }
        )

        serializer.is_valid(raise_exception=True)

        ExhibitionService.create_submission(
            idea=idea,
            form=serializer.validated_data["form"],
            submitted_data=serializer.validated_data["data"],
            request=request,
        )

        return Response(
            {
                "message": "Exhibition form submitted successfully."
            },
            status=status.HTTP_201_CREATED
        )

#/////////////////////////// EXHIBITION PROJECTS LIST ////////////////////


class PublicExhibitionProjectsAPIView(APIView):

    permission_classes = [AllowAny] 

    def get(self, request):

        sector = request.query_params.get("sector")

        projects = ExhibitionPublicService.get_projects(sector)

        serializer = PublicExhibitionListSerializer(
            projects,
            many=True
        )

        return Response(serializer.data)

#//////////////////////////// EXHIBITION PROJECTS DETAILS /////////////////////////

class PublicExhibitionProjectDetailsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            submission = ExhibitionPublicService.get_project_details(pk)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        serializer = PublicExhibitionDetailsSerializer(submission)

        return Response(serializer.data)




#//////////////////////////// CREATE TEAM REQUEST VIEW ////////////////////////

class CreateTeamRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

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
    permission_classes = [IsAuthenticated,CanViewTeamCandidates]

    def get(self, request):

        data = IdeaService.get_suggested_volunteers(request.user)
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
            "has_team": idea.team_members.exists(),
            "current_team": [
                {
                    "user_id": m.user.id,
                    "name": m.user.full_name,
                    "email": m.user.email,
                    "can_message": True
                }
                for m in idea.team_members.select_related("user")
            ]
        })



#//////////////////// PROJECT DETAILS ///////////////////////

class ProjectDetailsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            data = IdeaService.get_project_details(
                request.user
            )

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=404
            )

        serializer = ProjectDetailsSerializer(
            data["idea"]
        )

        return Response({
            **serializer.data,
            "team_members": data["team_members"]
        })






#/////////////////////////// CONSULTANTS LIST ////////////////////////
#UNUSED
class ConsultantsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = IdeaService.get_consultants()
        return Response(data)
    

#///////////////////////// TEAM DASHBOARD ///////////////////////

class TeamDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = IdeaService.get_team_dashboard(request.user)
        return Response(data)




#///////////////////////// EDIT IDEA VIEW ///////////////////////////////////
#UNUSED

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
#UNUSED
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
    
#//////////////////////////// MY IDEA VIEW (DISPLAY IDEA INFO TO THE USER ) /////////////////////////////////////
#UNUSED
class MyIdeasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ideas = Idea.objects.filter(
            owner=request.user
        ).order_by("-created_at")

        serializer = MyIdeaListSerializer(ideas, many=True)
        return Response(serializer.data)

#//////////////////////////// INCUBATION PHASE //////////////////////////

class IncubationPhaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            data = IdeaService.get_incubation_data(request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(data)