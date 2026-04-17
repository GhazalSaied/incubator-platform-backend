from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Role, User
from core.permissions import IsAdminOrSecretary
from django.shortcuts import get_object_or_404
from .serializers import AdminUserSerializer,CreateUserSerializer
from .selectors import get_users
from rest_framework import status
from .services.user_management_service import AdminUserService


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
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض الادوار\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class RoleListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        roles = Role.objects.exclude(code="DIRECTOR")

        return Response([
            {
                "id": r.id,
                "name": r.name_ar
            }
            for r in roles
        ])   
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تحديث أدوار المستخدم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class UpdateUserRolesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    

    def put(self, request, user_id):

        user = get_object_or_404(User, id=user_id)

        role_ids = request.data.get("roles", [])

        AdminUserService.update_user_roles(user, role_ids)

        return Response({
            "message": "تم تحديث الأدوار بنجاح"
        })