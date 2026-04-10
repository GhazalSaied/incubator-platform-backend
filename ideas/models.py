from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# //////////////////// IDEA STATUS //////////////////////

class IdeaStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"

    PRE_ACCEPTED = "PRE_ACCEPTED", "Pre Accepted (Bootcamp)"

    BOOTCAMP = "BOOTCAMP", "In Bootcamp"
    BOOTCAMP_FAILED = "BOOTCAMP_FAILED", "Bootcamp Failed"

    EVALUATION = "EVALUATION", "In Evaluation"
    EVALUATED = "EVALUATED", "Evaluated"

    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"

    INCUBATION = "INCUBATION", "In Incubation"

    EXHIBITION = "EXHIBITION", "In Exhibition"

    GRADUATED_POSITIVE = "GRADUATED_POSITIVE", "Graduated (Positive)"
    GRADUATED_NEGATIVE = "GRADUATED_NEGATIVE", "Graduated (Negative)"


# //////////////////// TEAM STATUS //////////////////////

class TeamStatus(models.TextChoices):
    NO_TEAM = "no_team", "No Team"
    TEAM_BUILDING = "team_building", "Building Team"
    TEAM_FULL = "team_full", "Team Complete"
    IN_PROGRESS = "in_progress", "In Progress"


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
        max_length=50,
        choices=IdeaStatus.choices,
        default=IdeaStatus.DRAFT
    )

    team_status = models.CharField(
        max_length=50,
        choices=TeamStatus.choices,
        default=TeamStatus.NO_TEAM
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
    
    
    
#///////////////////////////////// TEAM REQUEST ///////////////////////////////

class TeamRequest(models.Model):

    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name="team_requests"
    )

    title = models.CharField(max_length=255)

    skill_required = models.CharField(max_length=255)

    members_needed = models.PositiveIntegerField()

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("APPROVED", "Approved"),
        ],
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

#////////////////////////  IDEA AUDIT LOG  ////////////////////////

class IdeaAuditLog(models.Model):

    idea = models.ForeignKey("Idea", on_delete=models.CASCADE, related_name="logs")

    from_status = models.CharField(max_length=50)
    to_status = models.CharField(max_length=50)

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)


#/////////////////////////// SUGGESTED VOLUNTEER /////////////////////

class SuggestedVolunteer(models.Model):
    team_request = models.ForeignKey(
        TeamRequest,
        on_delete=models.CASCADE,
        related_name="suggested_volunteers"
    )

    volunteer = models.ForeignKey(
        "volunteers.VolunteerProfile",
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)