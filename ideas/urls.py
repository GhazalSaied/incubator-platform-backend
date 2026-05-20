from django.urls import path
from .views import (  
                    CurrentSeasonPhaseAPIView,MyIdeasAPIView,
                    IdeaDashboardAPIView,
                    ExhibitionDashboardAPIView,
                    CreateExhibitionSubmissionAPIView,
                    CreateTeamRequestAPIView,
                    IdeaTeamAPIView,
                    TeamDashboardAPIView,
                    SuggestedVolunteersAPIView, 
                    PublicExhibitionProjectsAPIView,
                    PublicExhibitionProjectDetailsAPIView,
                    SubmissionFormAPIView,
                    SaveStepAPIView,
                    SubmitIdeaAPIView,
                    ProjectDetailsAPIView,
                
                    
                
                    )

urlpatterns=[

    path("current-phase/",CurrentSeasonPhaseAPIView.as_view()),
    path("my/", MyIdeasAPIView.as_view()), 
    
    #================== TEAM =========================
    path("team-request/", CreateTeamRequestAPIView.as_view()),
    path("team/", IdeaTeamAPIView.as_view()),
    path("team-dashboard/",TeamDashboardAPIView.as_view()),
    path("suggested-volunteers/", SuggestedVolunteersAPIView.as_view()),

   
    
    #================== EXHIBITION ==========================
    path("exhibition/dashboard/", ExhibitionDashboardAPIView.as_view()),
    path("exhibition/submit/", CreateExhibitionSubmissionAPIView.as_view()),
    path("exhibition-projects/", PublicExhibitionProjectsAPIView.as_view()),
    path("projects/<int:pk>/", PublicExhibitionProjectDetailsAPIView.as_view()),
    
    #=================== IDEA ===================================
    path("seasons/<int:season_id>/submission-form/",SubmissionFormAPIView.as_view()),
    path("seasons/<int:season_id>/save-step/",SaveStepAPIView.as_view()),
    path("seasons/<int:season_id>/submit-idea/",SubmitIdeaAPIView.as_view()),
    path("idea-dashboard/", IdeaDashboardAPIView.as_view()),
    
    #================= PROJECT DETAILS (VOLUNTEER+INCUBATOR)===============
    
    path("project-details/",ProjectDetailsAPIView.as_view(),)

]