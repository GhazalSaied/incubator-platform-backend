
from django.urls import path
from .views import AdminUserListView,CreateUserView

urlpatterns = [
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المستخدمين مع الادوار\\\\\\\\\\\\\\\\
    path("", AdminUserListView.as_view()),
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة مستخدم جديد مع دور\\\\\\\\\\\\\\\\
    path("create/", CreateUserView.as_view()),
]