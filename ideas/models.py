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
    sector = models.CharField(max_length=255,
    null=True,
    blank=True
)
    target_audience = models.CharField(max_length=255,
    null=True,
    blank=True
)
    bootcamp_status = models.CharField(
    max_length=20,
    choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ],
    default='pending'
)

    evaluation_status = models.CharField(
    max_length=20,
    choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ],
    default='pending'
)
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
    

    #  EXHIBITION FIELDS

    exhibition_image = models.ImageField(upload_to="exhibition/", null=True, blank=True)

    project_goal = models.TextField(null=True, blank=True)
    project_services = models.TextField(null=True, blank=True)

    owner_email = models.EmailField(null=True, blank=True)
    team_emails = models.TextField(null=True, blank=True)

    exhibition_date = models.DateTimeField(null=True, blank=True)


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
    SELECT_MULTIPLE = 'select_multiple'

    QUESTION_TYPES = [
        (TEXT, 'Text'),
        (NUMBER, 'Number'),
        (SELECT, 'Select (single)'),
        (SELECT_MULTIPLE, 'Select (multiple)'),
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
class FormQuestionChoice(models.Model):
    question = models.ForeignKey(
        FormQuestion,
        on_delete=models.CASCADE,
        related_name='choices'
    )

    value = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'value'],
                name='unique_choice_value_per_question'
            )
        ]
        ordering = ['order']

    def __str__(self):
        return self.label

#////////////////////////////////// TEAM MEMBER /////////////////////////

class TeamMember(models.Model):
    idea = models.ForeignKey(
        "Idea",
        on_delete=models.CASCADE,
        related_name="team_members"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=50,
        default="MEMBER"
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    
    
    
    
from . import phases

    