from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from common.models import BaseModel
from .managers import UserManager
import random
from datetime import timedelta
from django.utils import timezone
#/////////////////////////// USER MODEL /////////////////////////////////////

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    bio = models.TextField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)
    last_password_change = models.DateTimeField(null=True, blank=True)

    email_verified_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()
    @property
    def role_codes(self):
       now = timezone.now()
       return list(
            self.userrole_set.filter(is_active=True)
            .filter(
                models.Q(expires_at__isnull=True) |
                models.Q(expires_at__gt=now)
            )
            .select_related("role")
            .values_list("role__code", flat=True)
        )

    def get_permissions(self):
        if hasattr(self, "_cached_permissions"):
            return self._cached_permissions

    

        now = timezone.now()

        perms = Permission.objects.filter(
            rolepermission__role__userrole__user=self,
            rolepermission__role__userrole__is_active=True,
            is_active=True
        ).filter(
            models.Q(rolepermission__role__userrole__expires_at__isnull=True) |
            models.Q(rolepermission__role__userrole__expires_at__gt=now)
        ).values_list("code", flat=True).distinct()

        self._cached_permissions = set(perms)
        return self._cached_permissions
    def __str__(self):
        return self.email
    
    
#/////////////////////////// ROLE MODEL /////////////////////////////////////

class Role(BaseModel):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    is_system_role = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    is_volunteer_role = models.BooleanField(default=False)

    def __str__(self):
        return self.code

#///////////////////////////  USER ROLE /////////////////////////////////////

class UserRole(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )

    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'role')


#/////////////////////////// PASSWORD RESET OTP ////////////////////

class PasswordResetOTP(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate_otp():
        return str(random.randint(1000, 9999))
    
    
#/////////////////////////// PERMISSION MODEL /////////////////////////////////////

class Permission(models.Model):

    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    module = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

#/////////////////////////// ROLE PERMISSION /////////////////////////////////////

class RolePermission(models.Model):

    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'permission')
        
   #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ USER PERMISSION (FOR OVERRIDES) \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\     
class UserPermission(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    granted = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'permission')