from django.urls import path
from .views import BootcampSessionCreateView, BootcampSessionListView

urlpatterns = [
    #\\\عرض الجلسات \\\\\
    path("", BootcampSessionListView.as_view(), name="session-list"),
    #\\\\\\\انشاء جلسة للمعسكر\\\\\\\\
    path("<int:season_id>/create/", BootcampSessionCreateView.as_view(), name="session-create"),
]