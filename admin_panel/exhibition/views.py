from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from core.permissions import IsAdminOrSecretary, IsDirector
from ideas.models import ExhibitionForm, ExhibitionQuestion
from .services.management_service import ExhibitionAdminService
from .services.query_service import ExhibitionQueryService, ExhibitionSubmissionQueryService




#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\انشاء معرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class CreateExhibitionView(APIView):
   
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    def post(self, request):

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
    
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    def post(self, request):

        title = request.data.get("title")

        try:
            form = ExhibitionAdminService.create_form(title=title)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        return Response({"id": form.id, "title": form.title})
    
#\\\\\\\\\\\\\\\\\\\\\\\\\انشاء سؤال  للمعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionFormBuilderAPIView(APIView):
    
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    def put(self, request, form_id):

        form = get_object_or_404(ExhibitionForm, id=form_id)

        questions_data = request.data.get("questions", [])

        ExhibitionAdminService.sync_form(form, questions_data)

        return Response({
            "message": "تم حفظ الفورم بنجاح"
        })
#\\\\\\\\\\\\\\\\\\\\\\\\\معاينة بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionFormPreviewAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    def get(self, request, form_id):

        form = get_object_or_404(ExhibitionForm, id=form_id)

        data = ExhibitionQueryService.get_form_preview(form)

        return Response(data)
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\نشر بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


class PublishExhibitionFormAPIView(APIView):
    
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    def post(self, request, form_id):

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