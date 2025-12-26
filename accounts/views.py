from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer, LoginSerializer
from .models import User

#///////////////////////// REGISTER VIEW ///////////////////////


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

#/////////////////////// LOGIN VIEW ///////////////////////////


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer

