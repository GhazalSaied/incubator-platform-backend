from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

from accounts.models import Role, UserRole

User = get_user_model()


class AdminUserService:

    @staticmethod
    @transaction.atomic
    def create_user(*, full_name, email, password, role_code, created_by):

        # 🟢 إنشاء المستخدم
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name
        )

        # 🟢 فرض تغيير كلمة المرور (فقط لأنه admin-created)
        user.must_change_password = True
        user.save(update_fields=["must_change_password"])

        # 🟢 جلب الدور
        role = Role.objects.filter(code=role_code).first()
        if not role:
            raise ValidationError("الدور غير موجود")

        # 🟢 ربط الدور
        UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=created_by,
            is_active=True
        )

        return user