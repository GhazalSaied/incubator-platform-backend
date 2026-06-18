from django.urls import path
from .views import  CreateExhibitionView,ExhibitionFormBuilderView,ExhibitionFormPreviewAPIView, ExhibitionSubmissionDetailsAPIView, GraduatedProjectsAPIView,PublishExhibitionFormAPIView,SubmissionListAPIView,ExhibitionSubmissionDecisionAPIView,ExhibitionHistoryAPIView,ExhibitionProjectsAPIView 


urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\انشاء معرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("create/", CreateExhibitionView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\انشاء فورم المعرض\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/create/", ExhibitionFormBuilderView.as_view()),  
    #\\\\\\\\\\\\\\\\\\\\\\\\\معاينة بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/<int:form_id>/preview/", ExhibitionFormPreviewAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\نشر بطاقة المعرض \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("form/<int:form_id>/publish/", PublishExhibitionFormAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\طلبات البطاقات \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("submissions/", SubmissionListAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("submissions/<int:submission_id>/", ExhibitionSubmissionDetailsAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول او رفض الطلب \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("submissions/<int:submission_id>/decision/", ExhibitionSubmissionDecisionAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\سجل المعارض\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("history/", ExhibitionHistoryAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل معرض معين\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:exhibition_id>/details/", ExhibitionProjectsAPIView.as_view()),
    path(
        "publicprojects/graduated/",
        GraduatedProjectsAPIView.as_view(),
        name="graduated-public-projects"
    ),         
]                 