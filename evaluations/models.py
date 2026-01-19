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
