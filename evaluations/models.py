from django.db import models
from django.conf import settings

from common.models import BaseModel
from ideas.models import Idea, Season

User = settings.AUTH_USER_MODEL


# /////////////////////////// CRITERIA ///////////////////////////

class EvaluationCriterion(BaseModel):
    """
    معيار تقييم ثابت تديره الإدارة
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField(default=5)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


# /////////////////////////// EVALUATION ///////////////////////////

class Evaluation(BaseModel):
    """
    تقييم واحد لفكرة واحدة من مقيم واحد
    """

    evaluator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evaluations"
    )

    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name="evaluations"
    )

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="evaluations",
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("evaluator", "idea")

    def __str__(self):
        return f"Evaluation #{self.id}"


# /////////////////////////// SCORES ///////////////////////////

class EvaluationScore(BaseModel):
    """
    درجة معيار واحد ضمن تقييم
    """

    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name="scores"
    )

    criterion = models.ForeignKey(
        EvaluationCriterion,
        on_delete=models.CASCADE,
        related_name="scores"
    )

    score = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    

    class Meta:
        unique_together = ("evaluation", "criterion")

    def __str__(self):
        return f"{self.criterion} - {self.score}"

#/////////////////////////// INCUBATION REVIEW /////////////////////////

class IncubationReview(BaseModel):

    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    meeting_date = models.DateTimeField()

    progress_score = models.FloatField(null=True, blank=True)

    notes = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.idea} - {self.meeting_date}"

#\\\\\\ IDEA EVALUATTOR\\\\\\

class IdeaEvaluator(BaseModel):
    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name="assigned_evaluators"
    )

    evaluator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_ideas"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )

    class Meta:
        unique_together = ("idea", "evaluator")
        
        
#\\\\\\\طلب انضمام للتقييم \\\\
class IdeaEvaluatorRequest(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
#\\\\\جلسة التقييم \\\\
class EvaluationSession(models.Model):
    idea = models.ForeignKey(
        "ideas.Idea",
        on_delete=models.CASCADE,
        related_name="evaluation_sessions"
    )

    scheduled_at = models.DateTimeField()

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"{self.idea.title} - {self.scheduled_at}"
    
    
    
#\\\\نموذج التقييم\\\
class EvaluationTemplate(models.Model):
    title = models.CharField(max_length=255)

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
    
    
#\\\\ربط النموذج مع المعايير \\\\
class EvaluationTemplateCriterion(models.Model):
    template = models.ForeignKey(
        EvaluationTemplate,
        on_delete=models.CASCADE,
        related_name="criteria"
    )

    criterion = models.ForeignKey(
        EvaluationCriterion,
        on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("template", "criterion")
        ordering = ["order"]

    def __str__(self):
        return f"{self.template} - {self.criterion}"
    
    
    
    
    
