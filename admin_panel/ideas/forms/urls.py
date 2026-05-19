from django.urls import path
from .views import (
    SeasonFormDesignAPIView,
    FormBuilderAPIView
)

urlpatterns = [
    path("<int:season_id>/builder/",FormBuilderAPIView.as_view()),
    #عرض النموذج مع مراعاة المرحلة 
    path("<int:pk>/form-design/",SeasonFormDesignAPIView.as_view(),name="season-form-design"),
    
]