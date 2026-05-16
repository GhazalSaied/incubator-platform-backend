# statistics/urls.py

from django.urls import path

from .views import (
    AdminBroadcastAPIView,
    CurrentSeasonStatisticsAPIView,
    ExpertiseStatisticsAPIView,
    GraduatedProjectsChartAPIView,
    LifecycleStatisticsAPIView,
    OverviewStatisticsAPIView,
    SeasonComparisonAPIView,
    SectorStatisticsAPIView
)

urlpatterns = [

    path("statistics/overview/<int:season_id>/",OverviewStatisticsAPIView.as_view(),name="overview-statistics"),
    path("statistics/lifecycle/<int:season_id>/",LifecycleStatisticsAPIView.as_view(),name="lifecycle-statistics"),
    path("statistics/sectors/<int:season_id>/",SectorStatisticsAPIView.as_view(),name="sector-statistics"),
    path("statistics/expertise/",ExpertiseStatisticsAPIView.as_view(),name="expertise-statistics"),
    path("statistics/seasons-comparison/",SeasonComparisonAPIView.as_view(),name="seasons-comparison"),
    path("statistics/current-season/",CurrentSeasonStatisticsAPIView.as_view(),name="current-season-statistics"),
    path("statistics/graduated-projects-chart/",GraduatedProjectsChartAPIView.as_view(),name="graduated-projects-chart"),
    path("notifications/broadcast/",AdminBroadcastAPIView.as_view()),
    

]