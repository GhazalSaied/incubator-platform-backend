from django.db import models
from django.conf import settings
from django.db.models import Q


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

#\\\\\\\\\\\\\\\\\\season status\\\\\\\\\\\\\\\\\\

class SeasonStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PUBLISHED = "PUBLISHED", "Published"
    CLOSED = "CLOSED", "Closed"

    
# ////////////////////// SEASONS /////////////////////////

class Season(models.Model):
    name = models.CharField(max_length=100)
    is_open = models.BooleanField(default=False)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=SeasonStatus.choices, default=SeasonStatus.DRAFT
    )

    start_date = models.DateField()
    end_date = models.DateField()
    exhibition_datetime = models.DateTimeField(null=True, blank=True)

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
    description = models.TextField(null=True, blank=True)

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
    sector = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    target_audience = models.TextField(null=True, blank=True)

    # editing due to state 

    def can_be_edited(self):
        return self.status == IdeaStatus.DRAFT

    def __str__(self):
        return self.title
    


#///////////////////// FORM STEPS ////////////////////

class FormStep(models.Model):
    form = models.ForeignKey(
        "IdeaForm",
        on_delete=models.CASCADE,
        related_name="steps"
    )

    title = models.CharField(max_length=255)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("form", "order")

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
    SELECT_MULTIPLE = 'select_multiple'
    LIST_TEXT = 'list_text'

    QUESTION_TYPES = [
        (TEXT, 'Text'),
        (NUMBER, 'Number'),
        (SELECT, 'Select (single)'),
        (SELECT_MULTIPLE, 'Select (multiple)'),
        (BOOLEAN, 'Yes / No'),
        (LIST_TEXT, 'List Text'),
    ]

    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"

    QUESTION_SOURCE_CHOICES = [
    (STATIC, "Static"),
    (DYNAMIC, "Dynamic"),
    ]

    STATIC_TITLE = "title"
    STATIC_DESCRIPTION = "description"
    STATIC_TARGET_AUDIENCE = "target_audience"
    STATIC_SECTOR = "sector"

    STATIC_FIELD_CHOICES = [
        (STATIC_TITLE, "Title"),
        (STATIC_DESCRIPTION, "Description"),
        (STATIC_TARGET_AUDIENCE, "Target Audience"),
        (STATIC_SECTOR, "Sector"),
    ]

    form = models.ForeignKey(
        IdeaForm,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    step = models.ForeignKey(
    FormStep,
    on_delete=models.CASCADE,
    related_name="questions",
    null=True,
    )

    source = models.CharField(
    max_length=20,
    choices=QUESTION_SOURCE_CHOICES,
    default=DYNAMIC
    )

    static_field = models.CharField(
        max_length=50,
        choices=STATIC_FIELD_CHOICES,
        null=True,
        blank=True
    )

    key = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    placeholder = models.CharField(max_length=255, null=True, blank=True)
    help_text = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=['form', 'key'],
                name='unique_question_key_per_form'
            ),
            models.UniqueConstraint(
                fields=['form', 'static_field'],
                condition=Q(source='STATIC'),
                name='unique_static_field_per_form'
            )
        ]

    def __str__(self):
        return self.label
    
#///////////////// FORM OUESTIONS CHOICE ////////////////////

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

    skill_required = models.JSONField(default=list,blank=True)

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
    reason = models.TextField(null=True, blank=True)


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
    
    
 #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ EXHIBITION FORM \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  
 
class ExhibitionForm(models.Model):
    season = models.OneToOneField(
        "ideas.Season",
        on_delete=models.CASCADE,
        related_name="exhibition_form"
    )

    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ EXHIBITION QUESTIONS \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExhibitionQuestion(models.Model):

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
        ExhibitionForm,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    key = models.CharField(max_length=100)
    label = models.CharField(max_length=255)

    type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES
    )

    required = models.BooleanField(default=False)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['form', 'key'],
                name='unique_exhibition_question_key_per_form'
            )
        ]

    def __str__(self):
        return self.label
 #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ EXHIBITION QUESTION OPTIONS \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   
 
class ExhibitionQuestionOption(models.Model):

    question = models.ForeignKey(
        ExhibitionQuestion,
        on_delete=models.CASCADE,
        related_name="options"
    )

    value = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.label
    
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ExhibitionSubmission\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    
class ExhibitionSubmission(models.Model):

    project = models.ForeignKey(Idea, on_delete=models.CASCADE)
    form = models.ForeignKey(ExhibitionForm, on_delete=models.CASCADE)

    data = models.JSONField()  # إجابات الفورم

    status = models.CharField(
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )
    message = models.TextField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)