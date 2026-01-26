from django.db import models
from .models import Season  


#///////////////////////////// SEASON PHASE //////////////////////////////////


class SeasonPhase(models.Model):
    SUBMISSION = "SUBMISSION"
    BOOTCAMP = "BOOTCAMP"
    EVALUATION = "EVALUATION"
    INCUBATION = "INCUBATION"
    EXHIBITION = "EXHIBITION"

    PHASE_CHOICES = [
        (SUBMISSION, "Submission"),
        (BOOTCAMP, "Bootcamp"),
        (EVALUATION, "Evaluation"),
        (INCUBATION, "Incubation"),
        (EXHIBITION, "Exhibition"),
    ]

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="phases"
    )

    phase = models.CharField(
        max_length=30,
        choices=PHASE_CHOICES
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("season", "phase")
        ordering = ["order"]

    def __str__(self):
        return f"{self.season.name} - {self.phase}"

