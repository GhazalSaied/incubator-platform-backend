from django.db import models

# Create your models here.
from common.models import BaseModel
from django.core.exceptions import ValidationError
from accounts.models import User
from ideas.phases import SeasonPhase
from ideas.models import Idea


class BootcampSession(BaseModel):
    phase = models.ForeignKey(
        SeasonPhase,
        on_delete=models.CASCADE,
        related_name='bootcamp_sessions'
    )

    title = models.CharField(max_length=255)

    trainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="session_as_trainer"
    )

    location = models.CharField(max_length=255,null=True)
    tasks = models.TextField(null=True)
    date = models.DateField(null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['start_time']
        
        
    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("وقت البداية لازم يكون قبل النهاية")
        
    def save(self, *args, **kwargs):
        self.clean()  # تشغيل التحقق دائماً
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
 
    
class BootcampAttendance(BaseModel):
    session = models.ForeignKey(BootcampSession, on_delete=models.CASCADE, related_name='attendance')

    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='attendance')

    status = models.CharField(
        choices=[
            ('present', 'Present'),
            ('absent', 'Absent'),
        ],
        max_length=10
    )

    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        unique_together = ('session', 'idea')
    
    def __str__(self):
        return f"{self.idea} - {self.session} - {self.status}"
    
    

class BootcampAbsenceRequest(BaseModel):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE,related_name='absence_requests')

    session = models.ForeignKey(BootcampSession, on_delete=models.CASCADE, related_name='absence_requests')

    reason = models.TextField()

    status = models.CharField(
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
        max_length=10
    )

    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('session', 'idea')
    
    def __str__(self):
        return f"{self.idea} - {self.session} - {self.status}"
    
    
class BootcampDecision(BaseModel):
    DECISION_CHOICES = [
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    idea = models.OneToOneField(
        Idea,
        on_delete=models.CASCADE,
        related_name='bootcamp_decision'
    )
    
    attendance_rate = models.FloatField()
    
    decision = models.CharField(
        max_length=10,
        choices=DECISION_CHOICES
    )
    
    
    decision_note = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.idea} - {self.decision}"
    
    
