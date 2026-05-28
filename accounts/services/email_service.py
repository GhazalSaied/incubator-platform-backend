from django.conf import settings
from django.core.mail import send_mail


class EmailService:

    @staticmethod
    def send_password_reset_otp(email, otp):

        send_mail(
            subject="رمز إعادة تعيين كلمة المرور",
            message=f"رمز التحقق الخاص بك هو: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )