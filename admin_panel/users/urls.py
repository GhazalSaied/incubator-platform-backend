
from django.urls import path

from admin_panel.evaluations.views import AcceptIdeaView, RejectIdeaView
from admin_panel.ideas.views import IdeaDetailsAPIView
from admin_panel.volunteers.views import VolunteerDetailsView
from .views import AdminUserListView,CreateUserView,RoleListAPIView,UpdateUserRolesAPIView,FreezeUserAPIView,UserDetailsAPIView, WorkshopDetailsForVolunteerView,WorkshopActionView

urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المستخدمين مع الادوار\\\\\\\\\\\\\\\\
    path("", AdminUserListView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة مستخدم جديد مع دور\\\\\\\\\\\\\\\\
    path("create/", CreateUserView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض الادوار\\\\\\\\\\\\\\\\
    path("roles/", RoleListAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\تحديث أدوار المستخدم \\\\\\\\\\\\\\\\\
    path("<int:user_id>/roles/", UpdateUserRolesAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تجميد مستخدم\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:user_id>/freeze/", FreezeUserAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\عرض تفاصيل المستخددم حسب الدور \\\\\\\\\\\\\\\\\
    path("<int:user_id>/details/", UserDetailsAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\زر عرض تفاصيل الفكرةموجود في ideas\\\\\\\\\\\\\\\\\\\\\\\
    path("ideas/<int:pk>/details/", IdeaDetailsAPIView.as_view(), name="idea-details"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\زر قبول فكرة موجود في evaluations\\\\\\\\\\\\\\\\\\\\\\\
    path("evaluations/accept-idea/<int:idea_id>/",AcceptIdeaView.as_view(),name="accept-idea"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\زر رفض فكرة موجود في evaluations\\\\\\\\\\\\\\\\\\\\\\\
    path("evaluations/reject-idea/<int:idea_id>/",RejectIdeaView.as_view(),name="reject-idea"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\زر عرض تفاصيل المتطوع موجود في volunteers\\\\\\\\\\\\\\\\\\\\\\\
    path("volunteers/volunteers/<int:volunteer_id>/", VolunteerDetailsView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض تفاصيل المهمة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("workshops/<int:workshop_id>/details/", WorkshopDetailsForVolunteerView.as_view(), name="workshop-details"),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\قبول او رفض مهمة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("workshops/<int:workshop_id>/action/", WorkshopActionView.as_view(), name="workshop-action"),
    
]