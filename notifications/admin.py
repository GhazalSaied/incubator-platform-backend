from django.contrib import admin
from .models import Notification,NotificationTemplate
# Register your models here.
admin.site.register(Notification)
admin.site.register(NotificationTemplate)