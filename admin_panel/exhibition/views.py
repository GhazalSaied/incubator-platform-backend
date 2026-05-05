from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from ideas.models import ExhibitionForm, ExhibitionQuestion, ExhibitionSubmission, Season
from ideas.services.season_phase_service import SeasonPhaseService
from .services.management_service import ExhibitionAdminService, ExhibitionSubmissionManagementService
from .services.query_service import ExhibitionHistoryQueryService, ExhibitionQueryService, ExhibitionSubmissionQueryService




#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\انشاء معرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class CreateExhibitionView(APIView):
   
    def post(self, request):
        permissions= SeasonPhaseService.get_phase_permissions()
        if not permissions.get("can_create_exhibition", False):
            return Response({"error": "غير مسموح بإنشاء معرض في الوقت الحالي"}, status=403)

        date = request.data.get("date")
        time = request.data.get("time")

        try:
            season = ExhibitionAdminService.create_exhibition(
                date=date,
                time=time
            )
        except ValidationError as e:
            return Response({"error": e.message}, status=400)

        return Response({
            "message": "تم إنشاء المعرض بنجاح",
            "datetime": season.exhibition_datetime
        })
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\انشاء بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class CreateFormView(APIView):
    
    
    def post(self, request):
        permissions= SeasonPhaseService.get_phase_permissions()
        if not permissions.get("can_create_exhibition", False):
            return Response({"error": "غير مسموح بإنشاء بطاقة معرض في الوقت الحالي"}, status=403)


        title = request.data.get("title")

        try:
            form = ExhibitionAdminService.create_form(title=title)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        return Response({"id": form.id, "title": form.title})
    
#\\\\\\\\\\\\\\\\\\\\\\\\\انشاء سؤال  للمعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionFormBuilderAPIView(APIView):
    
    
    def put(self, request, form_id):
        permissions= SeasonPhaseService.get_phase_permissions()
        if not permissions.get("can_create_exhibition", False):
            return Response({"error": "غير مسموح بإنشاء بطاقة معرض في الوقت الحالي"}, status=403)


        form = get_object_or_404(ExhibitionForm, id=form_id)

        questions_data = request.data.get("questions", [])

        ExhibitionAdminService.sync_form(form, questions_data)

        return Response({
            "message": "تم حفظ الفورم بنجاح"
        })
#\\\\\\\\\\\\\\\\\\\\\\\\\معاينة بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionFormPreviewAPIView(APIView):
    
    def get(self, request, form_id):
        

        form = get_object_or_404(ExhibitionForm, id=form_id)

        data = ExhibitionQueryService.get_form_preview(form)

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\نشر بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


class PublishExhibitionFormAPIView(APIView):
    
    def post(self, request, form_id):
        permissions= SeasonPhaseService.get_phase_permissions()
        if not permissions.get("can_create_exhibition", False):
            return Response({"error": "غير مسموح بنشر بطاقة معرض في الوقت الحالي"}, status=403)



        form = get_object_or_404(ExhibitionForm, id=form_id)

        ExhibitionAdminService.publish_form(form)

        return Response({
            "message": "تم نشر البطاقة بنجاح"
        })
        
 #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات البطاقات\\\\\\\\\\\\\\\\\\\\\\\\\\\       
    
class SubmissionListAPIView(APIView):
    
    def get(self, request):

        data = ExhibitionSubmissionQueryService.list_submissions()

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض تفاصيل الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\

class SubmissionDetailsAPIView(APIView):
    
    def get(self, request, submission_id):

        submission = get_object_or_404(ExhibitionSubmission, id=submission_id)

        data = ExhibitionSubmissionQueryService.get_submission_details(submission)

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول او رفض الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class ExhibitionSubmissionDecisionAPIView(APIView):

    def post(self, request, submission_id):
        permissions = SeasonPhaseService.get_phase_permissions()
        if not permissions.get("can_decide_exhibition_card", False):
            return Response({"error": "غير مسموح باتخاذ قرار على بطاقة المعرض في الوقت الحالي"}, status=403)

        decision = request.data.get("decision")
        message = request.data.get("message")

        submission = (
            ExhibitionSubmissionManagementService
            .process_decision(
                submission_id=submission_id,
                decision=decision,
                admin_message=message,
                actor=request.user
            )
        )

        return Response({
            "detail": "تم اتخاذ القرار بنجاح",
            "status": submission.status
        })
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\سجل المعارض\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionHistoryAPIView(APIView):
    
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
        