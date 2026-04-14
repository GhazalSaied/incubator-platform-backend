from django.urls import path
from .views import ApproveVolunteerView, PendingVolunteersView, RejectVolunteerView, VolunteerDetailsView
urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع المعلقة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("pending/", PendingVolunteersView.as_view(), name="pending-volunteers"),
    path("volunteers/<int:volunteer_id>/", VolunteerDetailsView.as_view()),
    path("volunteers/<int:volunteer_id>/approve/", ApproveVolunteerView.as_view()),
    path("volunteers/<int:volunteer_id>/reject/", RejectVolunteerView.as_view()),
]   