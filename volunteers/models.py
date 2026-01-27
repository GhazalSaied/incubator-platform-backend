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

#//////////////////////////// ////////////////////////////////////////

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
