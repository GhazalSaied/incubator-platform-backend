from django.contrib.auth import logout
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken


from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
)


#///////////////////////// REGISTER VIEW ///////////////////////


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

#/////////////////////// LOGIN VIEW ///////////////////////////


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer

from django.contrib.auth import logout
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
)



# ///////////////// REGISTER VIEW ///////////////////////////


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



#//////////////////////  LOGIN VIEW  JWT /////////////////////////


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer


#/////////////////////////// USER PROFILE VIEW //////////////////////////////////////////

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
#///////////////////////// CHANGE PASSWORD VIEW //////////////////////////////


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"detail": "كلمة المرور القديمة غير صحيحة"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "تم تغيير كلمة المرور بنجاح"},
            status=status.HTTP_200_OK
        )
    
#///////////////////////// LOGOUT VIEW   ////////////////////////////

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass

        logout(request)
        return Response(
            {"detail": "تم تسجيل الخروج بنجاح"},
            status=status.HTTP_200_OK
        )

#///////////////////////// DELETE ACCOUNT VIEW ////////////////////////////

class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(
            {"detail": "تم حذف الحساب نهائياً"},
            status=status.HTTP_204_NO_CONTENT
        )

#///////////////////////// FORGOT PASSWORD VIEW PHASE2 ////////////////////////////

class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email=serializer.validated_data["email"]
        ).first()

        if not user:
            return Response(
                {"detail": "إذا كان الإيميل موجود سيتم إرسال رابط"},
                status=status.HTTP_200_OK
            )

        # لاحقاً:
        # - generate token
        # - send email

        return Response(
            {"detail": "تم إرسال طلب إعادة تعيين كلمة المرور"},
            status=status.HTTP_200_OK
        )