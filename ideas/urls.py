from django.urls import path
from .views import ( CurrentIdeaFormAPIView , IdeaCreateAPIView , 
                    IdeaUpdateAPIView , WithdrawIdeaView,
                    CurrentSeasonPhaseAPIView,MyIdeasAPIView,
                    IdeaDashboardAPIView,
                    IncubationPhaseAPIView,
                    ExhibitionPhaseAPIView,
                    UpdateExhibitionAPIView,
                    )

urlpatterns=[
    path('form/', CurrentIdeaFormAPIView.as_view()),
    path('create/', IdeaCreateAPIView.as_view()),
    path('<int:idea_id>/update/',IdeaUpdateAPIView.as_view()),
    path("<int:idea_id>/withdraw/", WithdrawIdeaView.as_view()),
    path("current-phase/",CurrentSeasonPhaseAPIView.as_view()),
    path("my/", MyIdeasAPIView.as_view()),
    path("dashboard/", IdeaDashboardAPIView.as_view()),
    path("incubation/", IncubationPhaseAPIView.as_view()),
    path("exhibition/", ExhibitionPhaseAPIView.as_view()),
    path("exhibition/update/", UpdateExhibitionAPIView.as_view()),

    
    
    

]