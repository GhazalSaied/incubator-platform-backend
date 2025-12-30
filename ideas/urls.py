from django.urls import path
from .views import ( CurrentIdeaFormAPIView , IdeaCreateAPIView , IdeaUpdateAPIView , WithdrawIdeaView)

urlpatterns=[
    path('form/', CurrentIdeaFormAPIView.as_view()),
    path('create/', IdeaCreateAPIView.as_view()),
    path('<int:idea_id>/update/',IdeaUpdateAPIView.as_view()),
    path("ideas/<int:idea_id>/withdraw/", WithdrawIdeaView.as_view()),
]