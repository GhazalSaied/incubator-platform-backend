from django.urls import path
from .views import BootcampSessionCreateView, BootcampSessionListView

urlpatterns = [
    path("", BootcampSessionListView.as_view(), name="session-list"),
    path("create/", BootcampSessionCreateView.as_view(), name="session-create"),
]