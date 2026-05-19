from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from .services import FormBuilderService
from core.permissions import CanManageSeason
from ideas.serializers import FormReadSerializer, SeasonFormDesignSerializer,FormBuilderSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from admin_panel.seasons.services.season_query_service import SeasonQueryService
from ideas.models import FormQuestionChoice, Season,IdeaForm


class FormBuilderAPIView(APIView):


    def get(self, request, season_id):

        season = get_object_or_404(
            Season,
            id=season_id
        )

        form = getattr(
            season,
            "form",
            None
        )

        if not form:
            return Response(
                {
                    "form": None
                },
                status=status.HTTP_200_OK
            )

        serializer = FormReadSerializer(
            form
        )

        return Response(
            serializer.data
        )

    # =====================================
    # PUT
    # =====================================

    def put(self, request, season_id):

        season = get_object_or_404(
            Season,
            id=season_id
        )

        serializer = FormBuilderSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        form = FormBuilderService.sync(
            season=season,
            data=serializer.validated_data
        )

        response_serializer = (
            FormReadSerializer(form)
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )

        

    
#\\\\\\\\\\\\\\\\\عرض النموذج المصمم للموسم مع مراعاة المرحل \\\\\\\\\\\\\\\\\\\\\\
class SeasonFormDesignAPIView(APIView):
    
    permission_classes = [IsAuthenticated, CanManageSeason]
    def get(self, request, pk):
        season = get_object_or_404(Season, pk=pk)

        data = SeasonQueryService.get_form_design_data(season)

        serializer = SeasonFormDesignSerializer(instance=data)

        return Response(serializer.data)