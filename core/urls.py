
from django.contrib import admin
from django.urls import path , include 

from core.views import MyDashboardAPIView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/',include('accounts.urls')),
    path('api/ideas/', include('ideas.urls')),
    path('api/evaluations/', include('evaluations.urls')),
    path("api/profile/", include("profiles.urls")),
    path("api/volunteers/", include("volunteers.urls")),
    path("api/messaging/", include("messaging.api.urls")),
    path("api/notifications/", include("notifications.urls")),
    path('api/bootcamp/',include('bootcamp.urls')),
    path("api/admin/", include("admin_panel.urls")),
    path(
    "api/chatbot/",
    include("chatbot.urls")
),


    # volunteer + ideaOwner | team member 
    path("me/dashboard/", MyDashboardAPIView.as_view())

   

    
]
# ==================================
# MEDIA FILES
# ==================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

