from django.urls import path
from .views import ( CurrentIdeaFormAPIView , IdeaCreateAPIView , 
                    IdeaUpdateAPIView , WithdrawIdeaView,
                    CurrentSeasonPhaseAPIView,MyIdeasAPIView,
                    IdeaDashboardAPIView,
                    IncubationPhaseAPIView,
                    ExhibitionDashboardAPIView,
                    CreateExhibitionSubmissionAPIView,
                    CreateTeamRequestAPIView,
                    IdeaTeamAPIView,
                    TeamDashboardAPIView,
                    SuggestedVolunteersAPIView,
                    ConsultantsAPIView,
                    PublicExhibitionProjectsAPIView,
                    PublicExhibitionProjectDetailsAPIView,

                    
                
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

    path("team-request/", CreateTeamRequestAPIView.as_view()),
    path("team/", IdeaTeamAPIView.as_view()),
    path("team-dashboard/",TeamDashboardAPIView.as_view()),
    path("suggested-volunteers/", SuggestedVolunteersAPIView.as_view()),
    path("consultants/", ConsultantsAPIView.as_view()),
    
    #================== EXHIBITION ==========================
    path("exhibition/dashboard/", ExhibitionDashboardAPIView.as_view()),
    path("exhibition/submit/", CreateExhibitionSubmissionAPIView.as_view()),
    path("exhibition-projects/", PublicExhibitionProjectsAPIView.as_view()),
    path("projects/<int:pk>/", PublicExhibitionProjectDetailsAPIView.as_view()),
    
    
    

]