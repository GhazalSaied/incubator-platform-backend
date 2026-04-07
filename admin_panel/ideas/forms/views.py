from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from ideas.serializers import IdeaFormSerializer, CreateQuestionSerializer,SeasonFormDesignSerializer,CreateChoiceSerializer,FormQuestion
from core.permissions import IsAdminOrSecretary
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.shortcuts import get_object_or_404
from admin_panel.seasons.services import SeasonAdminService
from ideas.models import FormQuestionChoice, Season,IdeaForm
from admin_panel.ideas.forms.services import FormBuilderService


#\\\\creat form\\\
class CreateFormAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request, season_id):

        serializer = IdeaFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        season = get_object_or_404(Season, id=season_id)

        SeasonAdminService.create_form(
            season,
            serializer.validated_data
        )

        return Response({"message": "تم إنشاء النموذج"})
    
   #\\\\\\\\\\\\\\\\\انشاء سؤال تعديل حذف\\\\\\\\\\\\\\\\\
class FormBuilderAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def put(self, request, season_id):

        season = get_object_or_404(Season, id=season_id)

        form = season.form

        questions_data = request.data.get("questions", [])

        FormBuilderService.save_form_builder(form, questions_data)

        return Response({
            "message": "تم حفظ النموذج بنجاح"
        })
        
        
#\\\\\\\\\\\\\\\\\معاينة النموذج\\\\\\\\\\\\\\\\\\\\\\\\
class FormPreviewAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, season_id):

        season = get_object_or_404(Season, id=season_id)

        form = season.form

        data = FormBuilderService.get_form_preview(form)

        return Response({
            "questions": data
        })
    
#\\\\\\\\\\\\\\\\\عرض النموذج المصمم للموسم مع مراعاة المرحل \\\\\\\\\\\\\\\\\\\\\\
class SeasonFormDesignAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, pk):
        season = get_object_or_404(Season, pk=pk)

        data = SeasonAdminService.get_form_design_data(season)

        serializer = SeasonFormDesignSerializer(instance=data)

        return Response(serializer.data)