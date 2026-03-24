from django.db import models
from django.contrib.auth import get_user_model

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

#////////////////////////// VOLUNTREE ACTIVITY /////////////////////////////////////////


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

    request_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES ,
        default=CONSULTATION
    )

    project_title = models.CharField(max_length=255)
    consultation_type = models.CharField(max_length=100)

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_title} - {self.volunteer.user.email}"
    

#//////////////////////////////// VolunteerJoinRequest /////////////////////////////////


class VolunteerJoinRequest(models.Model):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (PENDING, "قيد المراجعة"),
        (ACCEPTED, "مقبول"),
        (REJECTED, "مرفوض"),
    ]

    volunteer = models.ForeignKey(
        "VolunteerProfile",
        on_delete=models.CASCADE,
        related_name="join_requests"
    )

    # صاحب الطلب (صاحب الفكرة / المشروع)
    requester_name = models.CharField(max_length=255)
    requester_email = models.EmailField()

    project_title = models.CharField(max_length=255)

    description = models.TextField()

    # معلومات إضافية تظهر عند التفاصيل
    target_audience = models.TextField(blank=True)
    problem_statement = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_title} - {self.volunteer.user.email}"