from django.urls import path
from .views import (
    FormBuilderAPIView,
    CreateFormAPIView,
    FormPreviewAPIView,
    SeasonFormDesignAPIView
)

urlpatterns = [
    # إنشاء فورم
    path("<int:season_id>/create/", CreateFormAPIView.as_view(), name="form-create"),
    # انشاء سؤال 
    path("<int:season_id>/builder/",FormBuilderAPIView.as_view()),
    #عرض النموذج مع مراعاة المرحلة 
    path("<int:pk>/form-design/",SeasonFormDesignAPIView.as_view(),name="season-form-design"),
    #\\\\\\\\\\معاينة النموذج قبل النشر
    path("<int:season_id>/preview/",FormPreviewAPIView.as_view())
    
]