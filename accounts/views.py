from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from core.events import EventBus
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from accounts.services.email_service import EmailService

from .models import User, PasswordResetOTP
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    VerifyPasswordOtpSerializer,
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
    ResetPasswordConfirmSerializer
)



# ///////////////// REGISTER VIEW ///////////////////////////
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        refresh = RefreshToken.for_user(
            user
        )

        return Response(
            {
                "user": serializer.data,
                "access": str(
                    refresh.access_token
                ),
                "refresh": str(
                    refresh
                ),
                "roles": user.role_codes
            },
            status=status.HTTP_201_CREATED,
        )


#//////////////////////  LOGIN VIEW  JWT /////////////////////////


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.user  #  هون اليوزر

        #  تحقق تغيير كلمة المرور
        if user.must_change_password:
            return Response({
        **serializer.validated_data,
        "roles": user.role_codes,
        "force_password_change": True,
    }, status=status.HTTP_200_OK)

        return Response({**serializer.validated_data, "roles": user.role_codes}, status=status.HTTP_200_OK)

#/////////////////////////// USER PROFILE VIEW //////////////////////////////////////////

class UserProfileAPIView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        serializer = (
            UserProfileSerializer(
                request.user,
                context={
                    "request": request
                }
            )
        )

        return Response(
            serializer.data
        )

    def put(self, request):

        serializer = (
            UserProfileSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={
                    "request": request
                }
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )
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
        user.must_change_password = False
        user.last_password_change = timezone.now()
        user.save()

        return Response({
            "detail": "تم تغيير كلمة المرور بنجاح",
            "must_change_password": False
        }, status=status.HTTP_200_OK)
    
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

    
#////////////////////// FORGOT PASSWORD VIEW phase1 //////////////////////////


class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()

        # لا تكشف وجود المستخدم
        if not user:
            return Response(
                {"detail": "إذا كان الإيميل موجود سيتم إرسال رمز"},
                status=status.HTTP_200_OK
            )

        # حذف أي OTP سابق غير مستخدم
        PasswordResetOTP.objects.filter(user=user, is_used=False).delete()

        recent_otp = PasswordResetOTP.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).exists()

        if recent_otp:
            return Response(
                {"detail": "تم إرسال رمز مسبقاً، حاول بعد دقيقة"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        otp = PasswordResetOTP.generate_otp()

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # إرسال OTP 
        try:
            EmailService.send_password_reset_otp(
                email=email,
                otp=otp
            )
        except Exception as e:
            print("EMAIL ERROR:", e)
            return Response(
                {"detail": "فشل إرسال البريد الإلكتروني"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"detail": "تم إرسال رمز إعادة التعيين"},
            status=status.HTTP_200_OK
        )


#////////////////////////// VERIFY PASSWORD phase2  //////////////////////////

class VerifyPasswordOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = VerifyPasswordOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp_input = serializer.validated_data["otp"]

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"detail": "بيانات غير صحيحة"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=otp_input,
            is_used=False
        ).order_by("-created_at").first()

        if not otp_obj:
            return Response(
                {"detail": "OTP غير صحيح"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            return Response(
                {"detail": "OTP منتهي الصلاحية"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "OTP صحيح"},
            status=status.HTTP_200_OK
        )

#////////////////////////// RESET PASSWORD CONFIRM phase3 ////////////////////

class ResetPasswordConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ResetPasswordConfirmSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp_input = serializer.validated_data["otp"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"detail": "بيانات غير صحيحة"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=otp_input,
            is_used=False
        ).order_by("-created_at").first()

        if not otp_obj:
            return Response(
                {"detail": "OTP غير صحيح"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            return Response(
                {"detail": "OTP منتهي الصلاحية"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(password)
        user.must_change_password = False
        user.last_password_change = timezone.now()
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        return Response(
            {"detail": "تم تغيير كلمة المرور بنجاح"},
            status=status.HTTP_200_OK
        )

