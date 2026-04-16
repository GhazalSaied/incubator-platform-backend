from django.urls import path
from .views import ExhibitionFormBuilderAPIView, CreateExhibitionView, CreateFormView,ExhibitionFormPreviewAPIView,PublishExhibitionFormAPIView,SubmissionListAPIView,SubmissionDetailsAPIView,SubmissionDecisionAPIView 

urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\انشاء معرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("create/", CreateExhibitionView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\انشاء بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/create/", CreateFormView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\انشاء سؤال للمعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/<int:form_id>/questions/", ExhibitionFormBuilderAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\معاينة بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/<int:form_id>/preview/", ExhibitionFormPreviewAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\نشر بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/<int:form_id>/publish/", PublishExhibitionFormAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\طلبات البطاقات \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("submissions/", SubmissionListAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("submissions/<int:submission_id>/", SubmissionDetailsAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول او رفض الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("submissions/<int:submission_id>/decision/", SubmissionDecisionAPIView.as_view()),
]                 