# statistics/apis/admin/overview_statistics_api.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from core.permissions import CanManageSeason

from .serializers import AdminBroadcastSerializer
from ideas.models import Season

from .services import (
    AdminBroadcastService,
    CurrentSeasonStatisticsService,
    ExpertiseStatisticsService,
    GraduatedProjectsChartService,
    LifecycleStatisticsService,
    OverviewStatisticsService,
    SeasonComparisonService,
    SectorStatisticsService
)


class OverviewStatisticsAPIView(APIView):
    #permission_classes = [IsAuthenticated, CanManageSeason]

    def get(self, request):

        data = OverviewStatisticsService.get()

        return Response(data)




class LifecycleStatisticsAPIView(APIView):
    #permission_classes = [IsAuthenticated, CanManageSeason]

    def get(self, request):

        data = LifecycleStatisticsService.get()

        return Response(data)
    
    

class SectorStatisticsAPIView(APIView):
    #permission_classes = [IsAuthenticated, CanManageSeason]

    def get(self, request):

        data = SectorStatisticsService.get()

        return Response(data)
    
    

class ExpertiseStatisticsAPIView(APIView):
    #permission_classes = [IsAuthenticated,CanManageSeason]

    def get(self, request):

        data = ExpertiseStatisticsService.get()

        return Response(data)
    
    
    



class SeasonComparisonAPIView(APIView):
    #permission_classes = [IsAuthenticated,CanManageSeason]

    def get(self, request):

        data = (
            SeasonComparisonService.get()
        )

        return Response(data)
    
    


class CurrentSeasonStatisticsAPIView(APIView):
    #permission_classes = [IsAuthenticated,CanManageSeason]

    def get(self, request):

        data = (
            CurrentSeasonStatisticsService.get()
        )

        return Response(data)
    
    



class GraduatedProjectsChartAPIView(APIView):
    #permission_classes = [IsAuthenticated,CanManageSeason]

    def get(self, request):

        data = (
            GraduatedProjectsChartService.get()
        )

        return Response(data)
    
    
    



class AdminBroadcastAPIView(APIView):
    #permission_classes = [IsAuthenticated,CanManageSeason]

    def post(self, request):

        serializer = AdminBroadcastSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        sent_count = (
            AdminBroadcastService.send(
                target=serializer.validated_data["target"],

                message=serializer.validated_data["message"]
            )
        )

        return Response({
            "message": "تم إرسال الإشعار بنجاح",

            "sent_count": sent_count
        }, status=status.HTTP_200_OK)