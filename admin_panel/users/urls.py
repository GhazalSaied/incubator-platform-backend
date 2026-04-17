
from django.urls import path
from .views import AdminUserListView,CreateUserView,RoleListAPIView,UpdateUserRolesAPIView

urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المستخدمين مع الادوار\\\\\\\\\\\\\\\\
    path("", AdminUserListView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة مستخدم جديد مع دور\\\\\\\\\\\\\\\\
    path("create/", CreateUserView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض الادوار\\\\\\\\\\\\\\\\
    path("roles/", RoleListAPIView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\تحديث أدوار المستخدم \\\\\\\\\\\\\\\\\
    path("<int:user_id>/roles/", UpdateUserRolesAPIView.as_view()),
]