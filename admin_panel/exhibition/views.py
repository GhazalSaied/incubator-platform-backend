from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from core.permissions import CanDecideExhibition, CanManageExhibition
from ideas.models import ExhibitionForm, ExhibitionQuestion, ExhibitionSubmission, Season
from ideas.services.season_phase_service import SeasonPhaseService
from .services.management_service import ExhibitionAdminService, ExhibitionSubmissionManagementService
from .services.query_service import ExhibitionHistoryQueryService, ExhibitionQueryService, ExhibitionSubmissionQueryService, ProjectsService




#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\انشاء معرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class CreateExhibitionView(APIView):
    permission_classes = [
        IsAuthenticated,
        CanDecideExhibition
    ]

    def post(self, request):

        date = request.data.get("date")
        time = request.data.get("time")

        try:
            season = ExhibitionAdminService.create_exhibition(
                date=date,
                time=time
            )

        except ValidationError as e:

            detail = e.detail

            if isinstance(detail, list):
                detail = detail[0]

            return Response(
                {
                    "detail": str(detail)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "تم إنشاء المعرض بنجاح",
                "datetime": season.exhibition_datetime
            },
            status=status.HTTP_200_OK
        )
#\\\\\\\\\\\\\\\\\\\\\\\\\انشاء بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionFormBuilderView(APIView):

    def post(self, request):

        questions = request.data.get("questions", [])

        form = ExhibitionAdminService.save_form(
            questions_data=questions
        )

        return Response(
            {
                "message": "تم حفظ البطاقة بنجاح",
                "form_id": form.id
            },
            status=status.HTTP_200_OK
        )
#\\\\\\\\\\\\\\\\\\\\\\\\\معاينة بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionFormPreviewAPIView(APIView):
    
    permission_classes = [IsAuthenticated,CanManageExhibition]
    def get(self, request, form_id):
        

        form = get_object_or_404(ExhibitionForm, id=form_id)

        data = ExhibitionQueryService.get_form_preview(form)

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\نشر بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


class PublishExhibitionFormAPIView(APIView):
    
    permission_classes = [IsAuthenticated,CanDecideExhibition]
    def post(self, request, form_id):
        form = get_object_or_404(ExhibitionForm, id=form_id)

        ExhibitionAdminService.publish_form(form)

        return Response({
            "message": "تم نشر البطاقة بنجاح"
        })
        
 #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات البطاقات\\\\\\\\\\\\\\\\\\\\\\\\\\\       
    
class SubmissionListAPIView(APIView):
    permission_classes = [IsAuthenticated,CanManageExhibition]
    def get(self, request):

        data = ExhibitionSubmissionQueryService.list_submissions()

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض تفاصيل الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\
class ExhibitionSubmissionDetailsAPIView(APIView):

    def get(self, request, submission_id):

        submission = get_object_or_404(
            ExhibitionSubmission,
            id=submission_id
        )

        data = ExhibitionSubmissionQueryService.get_submission_details(
            submission
        )

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول او رفض الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class ExhibitionSubmissionDecisionAPIView(APIView):
    permission_classes = [IsAuthenticated, CanDecideExhibition]

    def post(self, request, submission_id):
        decision = request.data.get("decision")
        message = request.data.get("message")

        try:
            submission = (
                ExhibitionSubmissionManagementService
                .process_decision(
                    submission_id=submission_id,
                    decision=decision,
                    admin_message=message,
                    actor=request.user
                )
            )

        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "detail": "تم اتخاذ القرار بنجاح",
                "status": submission.status
            },
            status=status.HTTP_200_OK
        )
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\سجل المعارض\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):

        data = ExhibitionHistoryQueryService.list_exhibitions()

        return Response(data)
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل معرض معين\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class ExhibitionProjectsAPIView(APIView):
    
    def get(self, request, exhibition_id):

        season = get_object_or_404(Season, id=exhibition_id)

        search = request.GET.get("search")
        sector = request.GET.get("sector")

        data = ExhibitionHistoryQueryService.get_exhibition_projects(
            season=season,
            search=search,
            sector=sector
        )

        return Response(data)
       
       
class GraduatedProjectsAPIView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        projects = (
            ProjectsService
            .get_all_graduated_projects()
        )

        return Response(projects) 