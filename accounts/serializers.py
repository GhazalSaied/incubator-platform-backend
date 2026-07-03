from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



#//////////////////////////// USER REGISTER ////////////////////////////////


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'id',
            'full_name',
            'email',
            'password',
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name']
        )
        return user

#//////////////////////// USER LOGIN //////////////////////////


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)


        token['email'] = user.email
        token['full_name'] = user.full_name

        return token

#////////////////////// PROFILE SERIALIZER (display & edit) ////////////////////////////////////////

class UserProfileSerializer(
    serializers.ModelSerializer
):
    
    avatar_url = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = User

        fields = [
            "full_name",
            "email",
            "phone",
            "city",
            "bio",
            "avatar",
            "avatar_url",
            "must_change_password"
        ]

    def get_avatar_url(
        self,
        obj
    ):
        request = self.context.get(
            "request"
        )

        if obj.avatar:
            return request.build_absolute_uri(
                obj.avatar.url
            )

        return None

#//////////////////////// CHANGE PASSWORD SERIALIZER ///////////////////////////////////////

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value

#////////////////////////// FORGOT PASSWORD SERIALIZER  phase 1 ////////////////////////////////////

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

#///////////////////////// VERIFY PASSWORD phase2 ///////////////////////////////////

class VerifyPasswordOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

#/////////////////////////// RESET PASSWORD CONFIRM > هل نسيت كلمة المرور  phase3/////////////////////

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                "كلمتا المرور غير متطابقتين"
            )

        return data
    
