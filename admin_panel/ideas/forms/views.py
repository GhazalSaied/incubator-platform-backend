from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from core.permissions import CanManageSeason
from ideas.serializers import CreateFormSerializer, FormSerializer,CreateQuestionSerializer,SeasonFormDesignSerializer,CreateChoiceSerializer,FormQuestion

from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.shortcuts import get_object_or_404
from admin_panel.seasons.services.season_admin_service import SeasonAdminService
from admin_panel.seasons.services.season_query_service import SeasonQueryService
from ideas.models import FormQuestionChoice, Season,IdeaForm
from admin_panel.ideas.forms.services import FormBuilderService


#\\\\creat form\\\
class CreateFormAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManageSeason]
    def post(self, request, season_id):

        serializer = CreateFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        season = get_object_or_404(Season, id=season_id)

        FormBuilderService.create_form(
            season,
            serializer.validated_data
        )

        return Response({"message": "تم إنشاء النموذج"})
    
   #\\\\\\\\\\\\\\\\\انشاء سؤال تعديل حذف\\\\\\\\\\\\\\\\\
class FormBuilderAPIView(APIView):
    
    permission_classes = [IsAuthenticated, CanManageSeason]
    def put(self, request, season_id):

        season = get_object_or_404(Season, id=season_id)

        form = season.form

        questions_data = request.data.get("questions", [])

        FormBuilderService.save_form_builder(form, questions_data)

        return Response({
            "message": "تم حفظ النموذج بنجاح"
        })
        
        

    
#\\\\\\\\\\\\\\\\\عرض النموذج المصمم للموسم مع مراعاة المرحل \\\\\\\\\\\\\\\\\\\\\\
class SeasonFormDesignAPIView(APIView):
    
    permission_classes = [IsAuthenticated, CanManageSeason]
    def get(self, request, pk):
        season = get_object_or_404(Season, pk=pk)

        data = SeasonQueryService.get_form_design_data(season)

        serializer = SeasonFormDesignSerializer(instance=data)

        return Response(serializer.data)