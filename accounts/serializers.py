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

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "full_name",
            "phone",
            "city",
            "bio",
            "avatar",
        ]

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
