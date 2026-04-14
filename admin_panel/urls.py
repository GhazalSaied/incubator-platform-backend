from django.urls import path, include

urlpatterns = [
    path("seasons/", include("admin_panel.seasons.urls")),
    path("ideas/", include("admin_panel.ideas.urls")),
    path("bootcamp/", include("admin_panel.bootcamp.urls")),
    path("evaluations/", include("admin_panel.evaluations.urls")),
    path("incubations/", include("admin_panel.incubations.urls")),
    path("volunteers/", include("admin_panel.volunteers.urls")),
]