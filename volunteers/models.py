
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
    bio=models.TextField(blank=True)
    projects_count=models.PositiveIntegerField(null=True,blank=True)

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

    current_company = models.CharField(max_length=255, null=True, blank=True)
    specialization = models.CharField(max_length=255, null=True, blank=True)

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

    ONE_TIME="ONE_TIME"
    ONGOING="ONGOING"

    HELP_TYPE_CHOICES = [
        (ONE_TIME, "استشارة لمرة واحدة"),
        (ONGOING, "متابعة دورية"),
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

    help_type = models.CharField(
        max_length=20,
        choices=HELP_TYPE_CHOICES,
        null=True,
        blank=True
    )

    required_skill = models.CharField(max_length=100,null=True)
    
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
    

#/////////////////////// JOIN REQUEST ///////////////////////

class JoinRequest(models.Model):

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (PENDING, "قيد المراجعة"),
        (ACCEPTED, "مقبول"),
        (REJECTED, "مرفوض"),
    ]

    volunteer = models.ForeignKey(
        "volunteers.VolunteerProfile",
        on_delete=models.CASCADE,
        related_name="join_requests"
    )

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_join_requests"
    )

    idea = models.ForeignKey(
        "ideas.Idea",
        on_delete=models.CASCADE,
        related_name="join_requests"
    )

    team_request = models.ForeignKey(
        "ideas.TeamRequest",
        on_delete=models.CASCADE
    )

    description = models.TextField()
    tasks = models.TextField(max_length=100,null=True)
    required_skill = models.CharField(max_length=100,null=True)

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

    

    capacity = models.PositiveIntegerField()
    sessions = models.PositiveIntegerField(null=True)
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


#///////////////// VOLUNTEER VACATION ////////////////////////

class VolunteerVacation(models.Model):
    volunteer = models.ForeignKey(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="vacations"
    )

    start_day = models.CharField(max_length=15, choices=WeekDay.choices,null=True)
    end_day = models.CharField(max_length=15, choices=WeekDay.choices,null=True)
