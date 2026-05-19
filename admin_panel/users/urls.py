
from django.urls import path
from .views import ActivateUserAPIView, AddUserToIdeaAPIView, AdminUserListView, AdminUserProfileAPIView,CreateUserView, CurrentSeasonIdeasAPIView,RoleListAPIView, SendNotificationToUserAPIView,UpdateUserRolesAPIView,FreezeUserAPIView

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
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفعيل حساب\\\\\\\\\\\\\\\\\\\\\\
    path("<int:user_id>/activate/",ActivateUserAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ارسال اشعار للمستخدمين من الادمن\\\\\\\\\\\\\\\\\\\\\\
    path("<int:user_id>/send-notification/",SendNotificationToUserAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المشاريع\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("current-season-ideas/",CurrentSeasonIdeasAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة عضو لفريق فكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:user_id>/add-to-team/",AddUserToIdeaAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفاصيل المستخدم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    path("<int:user_id>/profile/",AdminUserProfileAPIView.as_view()),
]