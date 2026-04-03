from django.urls import path
from .views import IdeaOwnerProfileAPIView,ContactAdminAPIView

urlpatterns = [
    path("idea-owner/",IdeaOwnerProfileAPIView.as_view(), name="idea-owner-profile"),
    path("contact/", ContactAdminAPIView.as_view()),

            
        
       
    
]
