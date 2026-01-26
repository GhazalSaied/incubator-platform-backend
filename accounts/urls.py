from django.urls import path
from .views import RegisterAPIView, LoginAPIView , UserProfileAPIView , ChangePasswordAPIView , ForgotPasswordAPIView,DeleteAccountAPIView,LogoutAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/',UserProfileAPIView.as_view(),name='profile'),
    path('change-password/',ChangePasswordAPIView.as_view(),name='change-password'),
    path('logout/', LogoutAPIView.as_view(),name='logout'),
    path('delete-account/',DeleteAccountAPIView.as_view(),name='delete-account'),
    path('forgot-password/',ForgotPasswordAPIView.as_view(),name='forgot-password'),

]
