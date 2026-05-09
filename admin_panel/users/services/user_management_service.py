from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from accounts.models import Role, UserRole, User
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from volunteers.models import Workshop

User = get_user_model()


class AdminUserService:

    @staticmethod
    @transaction.atomic
    def create_user(*, full_name, email, password, role_code, created_by):

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name
        )

        user.must_change_password = True
        user.save(update_fields=["must_change_password"])

        role = Role.objects.filter(code=role_code).first()
        if not role:
            raise ValidationError("الدور غير موجود")

        UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=created_by,
            is_active=True
        )

        return user
    

    
    @staticmethod
    def update_user_roles(user, role_ids):

        roles = Role.objects.filter(id__in=role_ids)

        if roles.count() != len(role_ids):
            raise ValidationError("بعض الأدوار غير موجودة")

        with transaction.atomic():
        # احذف الأدوار القديمة
            UserRole.objects.filter(user=user).delete()

        # أضف الأدوار الجديدة
            UserRole.objects.bulk_create([
                UserRole(user=user, role=role)
                for role in roles
            ])

        return user
    
    

    @staticmethod
    @transaction.atomic
    def freeze_user(*, user: User, performed_by: User):

        # 1. تحقق: هل المستخدم أصلاً مجمّد؟
        if not user.is_active:
            raise ValidationError("الحساب مجمّد مسبقاً")

        # 2. تحقق: ما يسمح يجمد حاله
        if user.id == performed_by.id:
            raise ValidationError("لا يمكنك تجميد حسابك")

       
        user.is_active = False
        user.deactivated_at = timezone.now()  # اختياري إذا عندك حقل
        user.save(update_fields=["is_active"])

        return user
    
    
    
    
    


class WorkshopServices:
    @transaction.atomic
    @staticmethod
    def change_workshop_status(workshop_id, action):
        
        workshop = get_object_or_404(Workshop, id=workshop_id)

        if workshop.status != "PENDING":
            raise ValidationError("You can only act on pending workshops")

        if action == "accept":
            workshop.status = "ACCEPTED"

        elif action == "reject":
            workshop.status = "REJECTED"

        else:
            raise ValidationError("Invalid action")

        workshop.save()

        return {
            "id": workshop.id,
            "status": workshop.status
        }