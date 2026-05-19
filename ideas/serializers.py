from rest_framework import serializers
from .models import (Idea, FormQuestion, 
                     IdeaForm, Season,
                     TeamRequest,
                     FormQuestionChoice,
                     ExhibitionForm,
                     ExhibitionQuestion,
                     ExhibitionQuestionOption,
                     ExhibitionSubmission,
                     TeamMember,
                     FormStep
)
from ideas.services.season_phase_service import SeasonPhaseService



#============================
# STEPS FORM + CREATE IDEA 
#===========================

#///////////////////////////IDAE FORM SERIALIZER /////////////////////////////////

class FormQuestionChoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    label = serializers.CharField()
    order = serializers.IntegerField()


#///////////////////////// SUBMISSION QUESTION SERIALIZER ////////////////////

class SubmissionQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField()
    label = serializers.CharField()
    type = serializers.CharField()
    required = serializers.BooleanField()
    order = serializers.IntegerField()
    source = serializers.CharField()
    static_field = serializers.CharField(allow_null=True)
    placeholder = serializers.CharField(allow_null=True)
    help_text = serializers.CharField(allow_null=True)
    choices = FormQuestionChoiceSerializer(many=True)


#/////////////////////////// SUBMISSION STEP SERIALIZER ///////////////////////////

class SubmissionStepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    order = serializers.IntegerField()
    questions = SubmissionQuestionSerializer(many=True)


#///////////////////////////// SUBMISSION FORM SERIALIZER ///////////////////////

class SubmissionFormSerializer(serializers.Serializer):
    form_id = serializers.IntegerField()
    form_title = serializers.CharField()
    current_step = serializers.IntegerField()
    total_steps = serializers.IntegerField()
    completed_steps = serializers.ListField(
        child=serializers.IntegerField()
    )
    idea_status = serializers.CharField(allow_null=True)
    draft_data = serializers.DictField()
    steps = SubmissionStepSerializer(many=True)


#//////////////////////////// SAVE STEP /////////////////////

class SaveStepSerializer(serializers.Serializer):
    step = serializers.IntegerField(min_value=1)
    data = serializers.DictField()

#///////////////////////// SUBMIT IDEA SERIALIZER ///////////////////////

class SubmitIdeaSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

#==================== لهون نهاية كل شي الو علاقة بالخطوات لانشاء الفكرة ===================

class FormQuestionSerializer(serializers.ModelSerializer):
    choices = FormQuestionChoiceSerializer(many=True)
    class Meta:
        model = FormQuestion
        fields = ['id','key','label','type','required','order','choices','placeholder', 'help_text']


class IdeaFormSerializer(serializers.ModelSerializer):
    questions = FormQuestionSerializer(many=True)

    class Meta:
        model = IdeaForm
        fields = ['id', 'title', 'questions']






#/////////////////////////// IDEA DETAILS /////////////////////////////////

class IdeaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = [
            'id',
            'title',
            'description',
            'status',
            'answers',
            'created_at'
        ]




#//////////////////////////////IDEA LIST (VIEW ONLY)/////////////////////////////////////
#UNUSED
class MyIdeaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "status",
            "created_at",
        ]



#/////////////////////////// TEAM REQUEST SERIALIZER /////////////////////

class TeamRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamRequest
        fields = [
            "title",
            "skill_required",
            "members_needed",
            "description",
        ]
        


#///////////////////////////// EXHIBITIONS QUESTIONS OPTIONS ////////////////////

class ExhibitionQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExhibitionQuestionOption
        fields = [
            "value",
            "label",
            "order",
        ]


#/////////////////////////////// EXHIBITIONS QUESTIONS /////////////////////////

class ExhibitionQuestionSerializer(serializers.ModelSerializer):
    options = ExhibitionQuestionOptionSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = ExhibitionQuestion
        fields = [
            "id",
            "key",
            "label",
            "type",
            "required",
            "order",
            "options",
        ]


#//////////////////// EXHIBITION FORM DETAILS //////////////////

class ExhibitionFormDetailsSerializer(serializers.ModelSerializer):
    questions = ExhibitionQuestionSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = ExhibitionForm
        fields = [
            "id",
            "title",
            "is_active",
            "questions",
        ]


#/////////////////////// EXHIBITION SUBMISSION CREATE /////////////////////////

class ExhibitionSubmissionCreateSerializer(serializers.Serializer):
    data = serializers.JSONField()

    def validate(self, attrs):
        idea = self.context["idea"]
        request_user = self.context["request"].user

        if idea.owner_id != request_user.id:
            raise serializers.ValidationError(
                "Only the idea owner can submit exhibition form."
            )

        already_submitted = ExhibitionSubmission.objects.filter(
            project=idea
        ).exists()

        if already_submitted:
            raise serializers.ValidationError(
                "Exhibition form already submitted."
            )

        form = getattr(
            idea.season,
            "exhibition_form",
            None
        )

        if not form or not form.is_active:
            raise serializers.ValidationError(
                "No active exhibition form found."
            )

        attrs["form"] = form
        return attrs


#///////////////////////// ExhibitionList > تاب المشاريع ////////////////////////


class PublicExhibitionListSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    title = serializers.SerializerMethodField()
    sector = serializers.CharField(source="project.sector")
    team_members = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_title(self, obj):
        return obj.data.get("title")

    def get_team_members(self, obj):
        return obj.data.get("team_members", [])

    def get_owner(self, obj):
        return obj.project.owner.full_name
    
#/////////////////////////////// EXHIBITION DETAILS > عرض التفاصيل في تاب المشاريع /////////////

class PublicExhibitionDetailsSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    title = serializers.SerializerMethodField()
    sector = serializers.CharField(source="project.sector")

    team_members = serializers.SerializerMethodField()
    project_goal = serializers.SerializerMethodField()
    project_services = serializers.SerializerMethodField()
    emails = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()

    owner_id = serializers.IntegerField(source="project.owner.id")

    def get_title(self, obj):
        return obj.data.get("title")

    def get_team_members(self, obj):
        return obj.data.get("team_members", [])

    def get_project_goal(self, obj):
        return obj.data.get("project_goal")

    def get_project_services(self, obj):
        return obj.data.get("project_services", [])

    def get_emails(self, obj):
        return obj.data.get("emails", [])

    def get_owner_email(self, obj):
        return obj.data.get("owner_email")


# ////////////////////////////////////////////////////////////////
# SHARED PROJECT DETAILS SERIALIZER
# Used in multiple places across the platform
# ////////////////////////////////////////////////////////////////

class ProjectDetailsSerializer(serializers.ModelSerializer):
    """
    Unified project details serializer.

    Used for:
    - Evaluation assignments details
    - Incubation review details
    - Any shared project details screen
    """

    # Section 1 → Project Information
    project_title = serializers.CharField(source="title", read_only=True)
    editor_name = serializers.CharField(source="owner.full_name", read_only=True)
    product_type = serializers.SerializerMethodField()

    # Section 2 → Owner Personal Information
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)
    phone = serializers.SerializerMethodField()
    specialization = serializers.SerializerMethodField()
    email = serializers.CharField(source="owner.email", read_only=True)

    # Section 3 → Idea Information
    idea_title = serializers.CharField(source="title", read_only=True)
    target_audience = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    problem = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "project_title",
            "editor_name",
            "product_type",
            "owner_name",
            "phone",
            "specialization",
            "email",
            "idea_title",
            "target_audience",
            "description",
            "problem",
        ]

    def get_product_type(self, obj):
        return obj.answers.get("product_type")

    def get_phone(self, obj):
        return obj.answers.get("phone")

    def get_specialization(self, obj):
        return obj.answers.get("specialization")

    def get_problem(self, obj):
        return obj.answers.get("problem")


#//////////////////////////// EXHIBITION  /////////////////////////////
#unused
class ExhibitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Idea
        fields = [
            "title",
            "exhibition_image",
            "project_goal",
            "project_services",
            "contact_email"
        ]

#//////////////////////// IDEA FOR EVALUATER ///////////////////////
#unused

class IdeaForEvaluationSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)
    form = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "description",
            "status",
            "owner_name",
            "answers",
            "form",
            "created_at",
        ]

    def get_form(self, obj):
        season = getattr(obj, "season", None)
        if not season or not hasattr(season, "form"):
            return None

        return IdeaFormSerializer(season.form).data
    
#/////////////////////////// IDEA DASHBOARD SERIALIZER /////////////////////////
#UNUSED
class IdeaDashboardSerializer(serializers.Serializer):
    phase = serializers.CharField()
    progress = serializers.ListField()
    data = serializers.DictField()
    


        
 #\\\\\\\\\\\\\\\\\\SeasonStatusSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class SeasonStatusSerializer(serializers.Serializer):
    is_open = serializers.BooleanField()
    label = serializers.CharField()
    phase = serializers.CharField(allow_null=True)       
        

    
#\\\\\SeasonCreateSerializer\\\\\
class SeasonCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
#\\\\\\  SeasonPublishSerializer  \\\\

class SeasonPublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ["is_published"]

    def update(self, instance, validated_data):
        instance.is_published = True
        instance.save()
        return instance
    
    
    
#\\\\\\\\\\\\\\\ IdeaListSerialize \\\\\\\\\\\

class IdeaListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)

    class Meta:
        model = Idea
        fields = [
            "id",
            "title",
            "status",
            "owner_name",
            "created_at",
        ]
        
class IdeaRowSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project_name = serializers.CharField()
    submitted_by = serializers.CharField()
    submitted_at = serializers.DateTimeField()      
#\\\\\\\\\\\\\\\\\\\\\SeasonDetailsSerializer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class SeasonDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    ideas_count = serializers.IntegerField()
    phase = serializers.CharField()
    remaining_days = serializers.IntegerField(allow_null=True)
    evaluation_ideas_count = serializers.IntegerField(allow_null=True)

    #  الجديد
    ideas = IdeaRowSerializer(many=True)
    
class ChoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    label = serializers.CharField()
    order = serializers.IntegerField()


class QuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField()
    label = serializers.CharField()
    type = serializers.CharField()
    required = serializers.BooleanField()
    order = serializers.IntegerField()
    choices = ChoiceSerializer(many=True)


class FormSerializer(serializers.Serializer):
    title = serializers.CharField()
    questions = QuestionSerializer(many=True)
    

class SeasonInfoSerializer(serializers.Serializer):
    season_name = serializers.CharField()
    phase = serializers.CharField()
    ideas_count = serializers.IntegerField()

    remaining_days = serializers.IntegerField(required=False)
    evaluation_ideas_count = serializers.IntegerField(required=False)

    show_remaining_days = serializers.BooleanField()
    show_evaluation_count = serializers.BooleanField()

    
class SeasonFormDesignSerializer(serializers.Serializer):
    season_info = SeasonInfoSerializer()
    form = FormSerializer()
    
    



class SeasonReviewSerializer(serializers.Serializer):
    season_info = SeasonInfoSerializer()
    ideas = IdeaRowSerializer(many=True)   


from rest_framework import serializers


# =========================================
# CHOICES
# =========================================

class FormChoicePayloadSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)

    value = serializers.CharField()

    label = serializers.CharField()

    order = serializers.IntegerField()


# =========================================
# QUESTIONS
# =========================================

class FormQuestionPayloadSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)

    source = serializers.ChoiceField(
        choices=["STATIC", "DYNAMIC"]
    )

    static_field = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    key = serializers.CharField()

    label = serializers.CharField()

    type = serializers.ChoiceField(
        choices=[
            "text",
            "number",
            "select",
            "select_multiple",
            "boolean",
            "list_text"
        ]
    )

    required = serializers.BooleanField()

    order = serializers.IntegerField()

    placeholder = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    help_text = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    choices = FormChoicePayloadSerializer(
        many=True,
        required=False
    )


# =========================================
# STEPS
# =========================================

class FormStepPayloadSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)

    title = serializers.CharField()

    order = serializers.IntegerField()

    questions = FormQuestionPayloadSerializer(
        many=True
    )


# =========================================
# ROOT
# =========================================

class FormBuilderSerializer(serializers.Serializer):

    title = serializers.CharField()

    steps = FormStepPayloadSerializer(
        many=True
    )
    
    


# =========================================
# CHOICES
# =========================================

class FormChoiceReadSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = FormQuestionChoice

        fields = [
            "id",
            "value",
            "label",
            "order"
        ]


# =========================================
# QUESTIONS
# =========================================

class FormQuestionReadSerializer(
    serializers.ModelSerializer
):

    choices = FormChoiceReadSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = FormQuestion

        fields = [
            "id",
            "source",
            "static_field",
            "key",
            "label",
            "type",
            "required",
            "order",
            "placeholder",
            "help_text",
            "choices"
        ]


# =========================================
# STEPS
# =========================================

class FormStepReadSerializer(
    serializers.ModelSerializer
):

    questions = FormQuestionReadSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = FormStep

        fields = [
            "id",
            "title",
            "order",
            "questions"
        ]


# =========================================
# FORM
# =========================================

class FormReadSerializer(
    serializers.ModelSerializer
):

    steps = FormStepReadSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = IdeaForm

        fields = [
            "id",
            "title",
            "season",
            "steps"
        ]