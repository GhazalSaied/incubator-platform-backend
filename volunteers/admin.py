from django.contrib import admin
from .models import VolunteerProfile,VolunteerAvailability,ConsultationRequest
# Register your models here.
admin.site.register(VolunteerProfile)
admin.site.register(VolunteerAvailability)
admin.site.register(ConsultationRequest)
