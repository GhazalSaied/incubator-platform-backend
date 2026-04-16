from django.urls import path
from .views import ExhibitionFormBuilderAPIView, CreateExhibitionView, CreateFormView,ExhibitionFormPreviewAPIView

urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\انشاء معرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("create/", CreateExhibitionView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\انشاء بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/create/", CreateFormView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\انشاء سؤال للمعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/<int:form_id>/questions/", ExhibitionFormBuilderAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\معاينة بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/<int:form_id>/preview/", ExhibitionFormPreviewAPIView.as_view()),
]                 