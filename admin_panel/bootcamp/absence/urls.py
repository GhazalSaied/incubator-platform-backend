from django.urls import path
from .views import AbsenceRequestsListView, AbsenceDecisionView

urlpatterns = [
    # 🔹 كل طلبات الغياب
    path("", AbsenceRequestsListView.as_view(), name="absence-requests"),

    # 🔹 اتخاذ قرار على طلب غياب
    path("decide/", AbsenceDecisionView.as_view(), name="absence-decision"),
]