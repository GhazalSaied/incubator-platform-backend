from django.utils import timezone
from accounts.models import Role, UserRole


class RoleService:

    @staticmethod
    def assign_role(user, role_code, assigned_by=None, expires_at=None):
        role = Role.objects.get(code=role_code)

        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={
                "assigned_by": assigned_by,
                "expires_at": expires_at,
                "is_active": True
            }
        )

        if not created:
            # إذا كان موجود بس inactive → فعّلو
            user_role.is_active = True
            user_role.expires_at = expires_at
            user_role.save()

        return user_role

    @staticmethod
    def remove_role(user, role_code):
        UserRole.objects.filter(
            user=user,
            role__code=role_code
        ).update(is_active=False)