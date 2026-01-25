from django.urls import path
from .views import AdminDashboardStats

urlpatterns = [
    path('dashboard/stats/', AdminDashboardStats.as_view(), name='dashboard-stats'),
]