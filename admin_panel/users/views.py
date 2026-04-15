from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminOrSecretary

from .serializers import AdminUserSerializer,CreateUserSerializer
from .selectors import get_users
from rest_framework import status
from .services import AdminUserService


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):
        role_code = request.query_params.get("role")

        users = get_users(role_code=role_code)

        serializer = AdminUserSerializer(users, many=True)

        return Response(serializer.data)
 #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة مستخدم جديد مع دور\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   


class CreateUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = AdminUserService.create_user(
            full_name=serializer.validated_data["full_name"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            role_code=serializer.validated_data["role_code"],
            created_by=request.user
        )

        return Response({
            "message": "تم إنشاء المستخدم بنجاح",
            "user": {
                "id": user.id,
                "email": user.email
            }
        }, status=status.HTTP_201_CREATED)