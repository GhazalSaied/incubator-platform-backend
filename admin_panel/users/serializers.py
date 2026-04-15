from rest_framework import serializers
from accounts.models import User, UserRole, Role    


class AdminUserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "created_at",
            "roles",
            "status",
        ]

    def get_roles(self, obj):
        return [
            ur.role.code
            for ur in obj.userrole_set.filter(is_active=True)
        ]

    def get_status(self, obj):
        return "ACTIVE" if obj.is_active else "INACTIVE"
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة مستخدم جديد مع دور\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class CreateUserSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    role_code = serializers.CharField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("الإيميل مستخدم مسبقاً")
        return value.lower()

    def validate_role_code(self, value):
        if not Role.objects.filter(code=value).exists():
            raise serializers.ValidationError("الدور غير موجود")
        return value