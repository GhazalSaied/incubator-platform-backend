from django.urls import path
from .views import(ApproveVolunteerView, ApprovedVolunteersView, EvaluatorsView, PendingVolunteersView, RejectVolunteerView, RemoveEvaluatorRoleView, 
        SendInvitationToVolunteerView, SuggestVolunteersAPIView, TeamRequestDetailsAPIView, VolunteerDetailsView,TeamRequestOwnersAPIView,AvailableApprovedVolunteersView)
urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع المعلقة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("pending/", PendingVolunteersView.as_view(), name="pending-volunteers"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض تفاصيل طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:volunteer_id>/", VolunteerDetailsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:volunteer_id>/approve/", ApproveVolunteerView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\رفض طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:volunteer_id>/reject/", RejectVolunteerView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المتطوعين المقبولين \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ \
    path("approved/", ApprovedVolunteersView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\إرسال دعوة تقييم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:volunteer_id>/send-invitation/",SendInvitationToVolunteerView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("evaluators/", EvaluatorsView.as_view(), name="evaluators"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\إزالة دور المقيم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:volunteer_id>/remove-evaluator-role/",RemoveEvaluatorRoleView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات الفريق\\\\\\\\\\\\\\\\\\\\\\\\\
    path("team-request-owners/",TeamRequestOwnersAPIView.as_view(),name="team-request-owners"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض تفاصيل الطلب\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("team-requests/<int:pk>/",TeamRequestDetailsAPIView.as_view(),name="team-request-details"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المتطوعين المتاحين والمقبولين لاقتراحهم لطلب فريق\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("available-approved-volunteers/",AvailableApprovedVolunteersView.as_view(),name="available-approved-volunteers"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اقتراح متطوعين لطلب فريق\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:team_request_id>/suggest/",SuggestVolunteersAPIView.as_view())    
]   