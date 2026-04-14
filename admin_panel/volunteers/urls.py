from django.urls import path
from .views import ApproveVolunteerView, ApprovedVolunteersView, EvaluatorsView, PendingVolunteersView, RejectVolunteerView, RemoveEvaluatorRoleView, SendInvitationToVolunteerView, VolunteerDetailsView
urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع المعلقة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("pending/", PendingVolunteersView.as_view(), name="pending-volunteers"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض تفاصيل طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("volunteers/<int:volunteer_id>/", VolunteerDetailsView.as_view()),\
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("volunteers/<int:volunteer_id>/approve/", ApproveVolunteerView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\رفض طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("volunteers/<int:volunteer_id>/reject/", RejectVolunteerView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المتطوعين المقبولين \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ \
    path("volunteers/approved/", ApprovedVolunteersView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\إرسال دعوة تقييم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("volunteers/<int:volunteer_id>/send-invitation/",SendInvitationToVolunteerView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("evaluators/", EvaluatorsView.as_view(), name="evaluators"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\إزالة دور المقيم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("volunteers/<int:volunteer_id>/remove-evaluator-role/",RemoveEvaluatorRoleView.as_view())
    
]   