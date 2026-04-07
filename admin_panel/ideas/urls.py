from django.urls import path,include
from .views import IdeaDetailsAPIView,SeasonReviewAPIView

urlpatterns = [
    path("forms/", include("admin_panel.ideas.forms.urls")),
    #\\\مراجعة الطلبات
    path("<int:pk>/review-submissions/", SeasonReviewAPIView.as_view()),
    #\\\\عرض تفاصيل الطلب
    path("<int:pk>/details/", IdeaDetailsAPIView.as_view(), name="idea-details"),
]