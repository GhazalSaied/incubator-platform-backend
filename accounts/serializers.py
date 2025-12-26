from rest_framework import serializers
from .models import User
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


