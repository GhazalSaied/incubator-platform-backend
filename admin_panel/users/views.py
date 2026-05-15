from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Role, User
from django.shortcuts import get_object_or_404

from ideas.models import Idea
from .serializers import AddTeamMemberSerializer, AdminUserSerializer,CreateUserSerializer, SendUserNotificationSerializer, WorkshopActionSerializer
from rest_framework import status
from .services.user_management_service import AdminUserService, TeamMemberAdminService, WorkshopServices, AdminNotificationService
from .services.query_service import UsersQueryService, UserProfileService
from django.core.exceptions import ValidationError

class AdminUserListView(APIView):
    
    def get(self, request):
        role_code = request.query_params.get("role")

        users = UsersQueryService.get_users(role_code=role_code)

        serializer = AdminUserSerializer(users, many=True)

        return Response(serializer.data)
 #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة مستخدم جديد مع دور\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   


class CreateUserView(APIView):
   
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
    
   
    def get(self, request):

        roles = Role.objects.exclude(code="ADMIN")

        return Response([
            {
                "id": r.id,
                "name": r.name_ar
            }
            for r in roles
        ])   
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تحديث أدوار المستخدم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class UpdateUserRolesAPIView(APIView):

    def put(self, request, user_id):

        user = get_object_or_404(
            User,
            id=user_id
        )

        role_ids = request.data.get("roles", [])

        if not isinstance(role_ids, list):
            raise ValidationError(
                "roles must be a list"
            )

        AdminUserService.update_user_roles(
            user=user,
            role_ids=role_ids,
            assigned_by=request.user
        )

        return Response({
            "message": "تم تحديث الأدوار بنجاح"
        })
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تجميد مستخدم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class FreezeUserAPIView(APIView):


    def post(self, request, user_id):

        user = get_object_or_404(
            User,
            id=user_id
        )

        AdminUserService.freeze_user(
            user=user,
            performed_by=request.user
        )

        return Response({
            "message": "تم تجميد الحساب بنجاح",

            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "status": "INACTIVE"
            }
        })
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تفعيل حساب مجمد \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class ActivateUserAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):

        user = get_object_or_404(
            User,
            id=user_id
        )

        AdminUserService.activate_user(
            user=user
        )

        return Response({
            "message": "تم تفعيل الحساب بنجاح",

            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "status": "ACTIVE"
            }
        })
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ارسال اشعار لمستخدم\\\\\\\\\\\\\\\\\\\\\\\\\

class SendNotificationToUserAPIView(APIView):

    def post(self, request, user_id):

        serializer = SendUserNotificationSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            id=user_id
        )

        AdminNotificationService.send_to_user(
            user=user,
            message=serializer.validated_data["message"],
            actor=request.user
        )

        return Response({
            "message": "تم إرسال الإشعار بنجاح"
        }, status=status.HTTP_200_OK)
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المشاريع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class CurrentSeasonIdeasAPIView(APIView):

    def get(self, request):

        data = UsersQueryService.get_current_ideas()

        return Response(data)      
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة عضو لفريق \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  
class AddUserToIdeaAPIView(APIView):

    def post(self, request, user_id):

        serializer = AddTeamMemberSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            id=user_id
        )

        idea = get_object_or_404(
            Idea,
            id=serializer.validated_data["idea_id"]
        )

        TeamMemberAdminService.add_member(
            user=user,
            idea=idea,
            added_by=request.user
        )

        return Response({
            "message": "تمت إضافة المستخدم للفريق بنجاح"
        }, status=status.HTTP_200_OK)  
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض تفاصيل المستخدم حسب الدور \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   
class AdminUserProfileAPIView(APIView):

    def get(self, request, user_id):

        user = get_object_or_404(
            User,
            id=user_id
        )

        data = UserProfileService.get_user_profile(user)

        return Response(data)