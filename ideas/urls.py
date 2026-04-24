from django.urls import path
from .views import ( CurrentIdeaFormAPIView , IdeaCreateAPIView , 
                    IdeaUpdateAPIView , WithdrawIdeaView,
                    CurrentSeasonPhaseAPIView,MyIdeasAPIView,
                    IdeaDashboardAPIView,
                    IncubationPhaseAPIView,
                    ExhibitionPhaseAPIView,
                    UpdateExhibitionAPIView,
                    CreateTeamRequestAPIView,
                    IdeaTeamAPIView,
                    TeamDashboardAPIView,
                    SuggestedVolunteersAPIView,
                    ConsultantsAPIView,
                    
                
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
    path("team-request/", CreateTeamRequestAPIView.as_view()),
    path("team/", IdeaTeamAPIView.as_view()),
    path("team-dashboard/",TeamDashboardAPIView.as_view()),
    path("suggested-volunteers/", SuggestedVolunteersAPIView.as_view()),
    path("consultants/", ConsultantsAPIView.as_view()),
    

    
    
    

]