
from django.contrib import admin
from django.urls import path , include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/',include('accounts.urls')),
    path('api/ideas/', include('ideas.urls')),
    path('api/', include('admin_dashboard.urls')),
    path('api/evaluations/', include('evaluations.urls')),

]
