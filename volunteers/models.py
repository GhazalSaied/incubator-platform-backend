
from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel
from ideas.models import Season
from django.conf import settings

User = settings.AUTH_USER_MODEL

User = get_user_model()

#/////////////////// AVAILABLE DAYS /////////////////////////////

class WeekDay(models.TextChoices):
    SUNDAY = "SUNDAY", "الأحد"
    MONDAY = "MONDAY", "الاثنين"
    TUESDAY = "TUESDAY", "الثلاثاء"
    WEDNESDAY = "WEDNESDAY", "الأربعاء"
    THURSDAY = "THURSDAY", "الخميس"
    FRIDAY = "FRIDAY", "الجمعة"
    SATURDAY = "SATURDAY", "السبت"


#//////////////////////////// VOLUNTREE PROFILE //////////////////////////


class VolunteerProfile(models.Model):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (PENDING, "قيد المراجعة"),
        (APPROVED, "مقبول"),
        (REJECTED, "مرفوض"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="volunteer_profile"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    residence = models.CharField(max_length=255)
    years_of_experience = models.PositiveIntegerField()
    primary_skills = models.TextField()
    additional_skills = models.TextField(blank=True)

    volunteer_type = models.CharField(
        max_length=100,
        help_text="استشارات، تقني، مدرب..."
    )

    availability_type = models.CharField(
        max_length=50,
        help_text="تعاون طويل / تعاون محدود"
    )

    motivation = models.TextField()
    cv = models.FileField(upload_to="volunteer_cvs/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Volunteer"


#//////////////////////////// VOLUNTEER AVAILABILITY ////////////////////////////////////////

class VolunteerAvailability(models.Model):
    volunteer = models.ForeignKey(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="availabilities"
    )

    day = models.CharField(
        max_length=15,
        choices=WeekDay.choices
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("volunteer", "day", "start_time", "end_time")

    def __str__(self):
        return f"{self.volunteer.user.email} - {self.day}"

#//////////////////////////////// ConsultationRequest ////////////////////////////////////////////

class ConsultationRequest(models.Model):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (PENDING, "قيد المراجعة"),
        (ACCEPTED, "مقبول"),
        (REJECTED, "مرفوض"),
    ]

    CONSULTATION = "CONSULTATION"
    JOIN_REQUEST = "JOIN"

    TYPE_CHOICES = [
        (CONSULTATION, "استشارة"),
        (JOIN_REQUEST, "انضمام لفريق"),
    ]

    volunteer = models.ForeignKey(
        "VolunteerProfile",
        on_delete=models.CASCADE,
        related_name="consultation_requests"
    )

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_consultation_requests",
        null=True,
        blank=True
    )

    idea = models.ForeignKey(
        "ideas.Idea",
        on_delete=models.CASCADE,
        related_name="consultation_requests"
       
    )

    request_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=CONSULTATION
    )

    team_request = models.ForeignKey(
        "ideas.TeamRequest",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
    

#//////////////////////////////// WORKSHOP //////////////////////


class Workshop(BaseModel):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    )

    title = models.CharField(max_length=255)

    category = models.CharField(max_length=100)  # تسويق - برمجة...

    description = models.TextField()
    objectives = models.TextField()

    target_audience = models.TextField()  # لمين مناسبة

    start_date = models.DateField()
    end_date = models.DateField()

    days = models.JSONField()  # ["Monday", "Wednesday"]

    time_from = models.TimeField()
    time_to = models.TimeField()

    duration = models.CharField(max_length=50)  # "2 hours"

    capacity = models.PositiveIntegerField()

    image = models.ImageField(upload_to="workshops/", null=True, blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="my_workshops"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return self.title


#//////////////////////// WORKSHOP REGISTRATION //////////////////

class WorkshopRegistration(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workshop_registrations"
    )

    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        unique_together = ("user", "workshop")



