from rest_framework import serializers
from accounts.models import User, UserRole, Role
from volunteers.models import VolunteerProfile    


class AdminUserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    volunteer_request_id = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "created_at",
            "roles",
            "status",
            "volunteer_request_id",
        ]
    def get_created_at(self, obj):

        if not obj.created_at:
            return None

        return obj.created_at.strftime("%d/%m/%Y")
    def get_roles(self, obj):
        return list({
        ur.role.code
        for ur in obj.userrole_set.all()
        if ur.is_active
    })

    def get_status(self, obj):
        return "ACTIVE" if obj.is_active else "INACTIVE"
    def get_volunteer_request_id(self, obj):
        request = VolunteerProfile.objects.filter(
        user=obj
    ).first()

        return request.id if request else None
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\اضافة مستخدم جديد مع دور\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class CreateUserSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=8,
        write_only=True
    )

    role_code = serializers.CharField(
    required=False,
    allow_null=True,
    allow_blank=True
)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["role_code"].choices = Role.objects.values_list(
            "code", "code"
        )

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("الإيميل مستخدم مسبقاً")

        return value

   
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\SendUserNotificationSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class SendUserNotificationSerializer(serializers.Serializer):

    message = serializers.CharField()

    def validate_message(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "الرسالة مطلوبة"
            )

        return value
    



class AddTeamMemberSerializer(serializers.Serializer):
    idea_id = serializers.IntegerField()

class WorkshopActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["accept", "reject"])