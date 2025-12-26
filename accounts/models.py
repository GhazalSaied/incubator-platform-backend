from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from common.models import BaseModel
from .managers import UserManager

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

    email_verified_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.email

#/////////////////////////// ROLE MODEL /////////////////////////////////////

class Role(BaseModel):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)

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
