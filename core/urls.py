
from django.contrib import admin
from django.urls import path , include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/',include('accounts.urls')),
    path('api/ideas/', include('ideas.urls')),
    path('api/evaluations/', include('evaluations.urls')),
    path("api/profile/", include("profiles.urls")),
    path("api/volunteers/", include("volunteers.urls")),
    path("api/messages/", include("messaging.urls")),
    path("api/notifications/", include("notifications.urls")),
    path('api/bootcamp/',include('bootcamp.urls')),
    path("api/admin/", include("admin_panel.urls")),


   

    
]


