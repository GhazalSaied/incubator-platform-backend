from django.db import models
from django.conf import settings

from common.models import BaseModel
from ideas.models import Idea, Season

User = settings.AUTH_USER_MODEL


#///////////////////////////

class EvaluationCriterion(BaseModel):
    """
    Represents a single evaluation criterion used by the evaluation committee.
    Managed by the administration.
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

#//////////////////////////


class Evaluation(BaseModel):
    """
    Represents one evaluation performed by one evaluator
    on one idea within a season.
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
        related_name="evaluations"
    )

    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("evaluator", "idea")

    def __str__(self):
        return f"Evaluation of {self.idea_id} by {self.evaluator_id}"
    

#////////////////////////


class EvaluationScore(BaseModel):
    """
    Stores the score for a single criterion within an evaluation.
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

    score = models.PositiveIntegerField()

    class Meta:
        unique_together = ("evaluation", "criterion")
