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
        unique_together = ("evaluator", "idea", "season")

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


#///////////////////////// EVALUATION INVITATION /////////////////////////

class EvaluationInvitation(BaseModel):
    """
    دعوة لمتطوع ليصبح مقيم ضمن لجنة تقييم
    """

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evaluation_invitations"
    )

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="evaluation_invitations"
    )

    expertise_field = models.CharField(max_length=255)

    meeting_date = models.DateTimeField()

    expected_duration = models.CharField(max_length=255)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.season}"
    

#//////////////////////////// EVALUATION ASSIGNMENT ///////////////////////

class EvaluationAssignment(BaseModel):
    """
    ربط المقيم مع فكرة لتقييمها
    """

    evaluator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_evaluations"
    )

    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name="evaluation_assignments"
    )

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="evaluation_assignments"
    )

    invitation = models.ForeignKey(
        EvaluationInvitation,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    meeting_date = models.DateTimeField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("evaluator", "idea", "season")

    def __str__(self):
        return f"{self.evaluator} - {self.idea}"


#\\\\\\\\\\\\\\\\\\\\\\\\\\ EVALUATION SETTINGS \\\\\\\\\\\\\\\\\\\\\\\\\\\
class EvaluationSettings(models.Model):

    is_published = models.BooleanField(default=False)
    

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Evaluation Settings"