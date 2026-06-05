from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError
from accounts.models import Role, UserRole, User
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from volunteers.models import Workshop
from accounts.role_service import RoleService
User = get_user_model()


class AdminUserService:

    @staticmethod
    @transaction.atomic
    def create_user(
    *,
    full_name,
    email,
    password,
    role_code=None,
    created_by
):

    # ✅ إنشاء المستخدم أولاً
        user = User.objects.create_user(
        email=email.strip().lower(),
        password=password,
        full_name=full_name.strip()
    )

        user.must_change_password = True
        user.save(update_fields=["must_change_password"])

    # ✅ إذا تم اختيار دور فقط
        if role_code:
            role = Role.objects.filter(
            code=role_code
        ).first()

            if not role:
               raise ValidationError(
                "الدور غير موجود"
            )

            RoleService.assign_role(
            user=user,
            role_code=role_code,
            assigned_by=created_by
        )

        return user
    
    

    @staticmethod
    @transaction.atomic
    def update_user_roles(
        *,
        user,
        role_ids,
        assigned_by=None
    ):

        roles = Role.objects.filter(id__in=role_ids)

        if roles.count() != len(role_ids):
            raise ValidationError(
                "بعض الأدوار غير موجودة"
            )

        
        new_role_codes = set(
            roles.values_list("code", flat=True)
        )

        current_role_codes = set(
            UserRole.objects.filter(
                user=user,
                is_active=True
            ).values_list(
                "role__code",
                flat=True
            )
        )

        # =========================
        # REMOVE ROLES
        # =========================

        roles_to_remove = (
            current_role_codes - new_role_codes
        )

        for role_code in roles_to_remove:

            RoleService.remove_role(
                user=user,
                role_code=role_code
            )

        # =========================
        # ASSIGN ROLES
        # =========================

        roles_to_add = (
            new_role_codes - current_role_codes
        )

        for role_code in roles_to_add:

            RoleService.assign_role(
                user=user,
                role_code=role_code,
                assigned_by=assigned_by
            )

        return user
    

    @staticmethod
    @transaction.atomic
    def freeze_user(*, user, performed_by=None):

        
        if performed_by and user.id == performed_by.id:
            raise ValidationError(
                "لا يمكنك تجميد حسابك"
            )

        
        if not user.is_active:
            raise ValidationError(
                "الحساب مجمد مسبقاً"
            )
        user.is_active = False
        user.save(update_fields=["is_active"])

        return user 
    

    @staticmethod
    @transaction.atomic
    def activate_user(*, user):

        if user.is_active:
            raise ValidationError(
                "الحساب مفعل مسبقاً"
            )

        user.is_active = True

        user.save(update_fields=["is_active"])

        return user   
    

from core.events import EventBus


class AdminNotificationService:

    @staticmethod
    def send_to_user(
        *,
        user,
        message,
        actor=None
    ):

        EventBus.emit(
            "admin_manual_notification",
            receiver=user,
            extra={
                "message": message
            },
            actor=actor
        )

        return True
    
from django.db import transaction
from django.core.exceptions import ValidationError

from ideas.models import (
    Idea,
    TeamMember,
    TeamStatus
)

class TeamMemberAdminService:

    @staticmethod
    @transaction.atomic
    def add_member(*, user, idea, added_by):

        if idea.owner_id == user.id:
            raise ValidationError("هذا المستخدم هو صاحب الفكرة بالفعل")

        exists = TeamMember.objects.filter(
            idea=idea,
            user=user
        ).exists()

        if exists:
            raise ValidationError("المستخدم عضو بالفعل ضمن الفريق")

        TeamMember.objects.create(
            idea=idea,
            user=user,
            role="MEMBER"
        )

        RoleService.assign_role(
            user=user,
            role_code="INCUBATOR",
            assigned_by=added_by
        )

        idea.team_status = TeamStatus.IN_PROGRESS
        idea.save(update_fields=["team_status"])


        return True
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