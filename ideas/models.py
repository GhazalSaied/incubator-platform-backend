from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# //////////////////// IDEA STATUS //////////////////////

class IdeaStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    INCUBATED = 'INCUBATED', 'Incubated'
    REJECTED = 'REJECTED', 'Rejected'
    WITHDRAWN = 'WITHDRAWN', 'Withdrawn'


# ////////////////////// SEASONS /////////////////////////

class Season(models.Model):
    name = models.CharField(max_length=100)
    is_open = models.BooleanField(default=False)

    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


# ////////////////////// IDEAS /////////////////////////

class Idea(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ideas'
    )

    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        related_name='ideas'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=IdeaStatus.choices,
        default=IdeaStatus.DRAFT
    )

    #  Dynamic form answers

    answers = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # editing due to state 

    def can_be_edited(self):
        return self.status in [
            IdeaStatus.DRAFT,
            IdeaStatus.SUBMITTED
        ]

    def __str__(self):
        return self.title


# ////////////////////// FORM /////////////////////////

class IdeaForm(models.Model):
    season = models.OneToOneField(
        Season,
        on_delete=models.CASCADE,
        related_name='form'
    )
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


# ////////////////////// Dynamic Questions /////////////////////////

class FormQuestion(models.Model):
    TEXT = 'text'
    NUMBER = 'number'
    SELECT = 'select'
    BOOLEAN = 'boolean'

    QUESTION_TYPES = [
        (TEXT, 'Text'),
        (NUMBER, 'Number'),
        (SELECT, 'Select'),
        (BOOLEAN, 'Yes / No'),
    ]

    form = models.ForeignKey(
        IdeaForm,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    key = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['form', 'key'],
                name='unique_question_key_per_form'
            )
        ]

    def __str__(self):
        return self.label
