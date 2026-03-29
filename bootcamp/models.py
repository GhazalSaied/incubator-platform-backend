from django.db import models

# Create your models here.

from django.core.exceptions import ValidationError
from accounts.models import User
from ideas.phases import SeasonPhase


class BootcampSession(models.Model):
    phase = models.ForeignKey(
        SeasonPhase,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    title = models.CharField(max_length=255)

    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bootcamp_sessions"
    )

    location = models.CharField(max_length=255)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def clean(self):
        # ✅ تحقق إنو المرحلة Bootcamp فقط
        if self.phase.phase != SeasonPhase.BOOTCAMP:
            raise ValidationError("يمكن إنشاء جلسات فقط ضمن مرحلة المعسكر (BOOTCAMP)")

        # ✅ تحقق من الوقت
        if self.start_time >= self.end_time:
            raise ValidationError("وقت البداية يجب أن يكون قبل وقت النهاية")

    def save(self, *args, **kwargs):
        self.clean()  # تشغيل التحقق دائماً
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title