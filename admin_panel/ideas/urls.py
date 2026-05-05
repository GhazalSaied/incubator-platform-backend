from django.urls import path,include
from .views import IdeaDetailsAPIView

urlpatterns = [
    path("forms/", include("admin_panel.ideas.forms.urls")),
    
    #\\\\عرض تفاصيل الطلب
    path("<int:pk>/details/", IdeaDetailsAPIView.as_view(), name="idea-details"),
]