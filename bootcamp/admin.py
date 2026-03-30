from django.contrib import admin
from .models import BootcampSession,BootcampAttendance,BootcampAbsenceRequest,BootcampDecision

# Register your models here.
admin.site.register(BootcampSession)
admin.site.register(BootcampAttendance)
admin.site.register(BootcampAbsenceRequest)
admin.site.register(BootcampDecision)