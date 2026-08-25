from rest_framework import serializers
from django.conf import settings
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

from rest_framework import serializers
from .models import TeamRequest


class TeamRequestSerializer(serializers.ModelSerializer):

    title = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "عنوان الفكرة مطلوب",
            "blank": "عنوان الفكرة لا يمكن أن يكون فارغاً",
        }
    )

    skill_required = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "الرجاء اختيار المهارة المطلوبة",
            "blank": "الرجاء اختيار المهارة المطلوبة",
        }
    )

    members_needed = serializers.IntegerField(
        required=True,
        error_messages={
            "required": "عدد المتطوعين مطلوب",
            "invalid": "عدد المتطوعين يجب أن يكون رقماً صحيحاً",
            "null": "عدد المتطوعين مطلوب",
        }
    )

    description = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "شرح الفكرة مطلوب",
            "blank": "شرح الفكرة لا يمكن أن يكون فارغاً",
        }
    )

    class Meta:
        model = TeamRequest
        fields = [
            "title",
            "skill_required",
            "members_needed",
            "description",
        ]

    def validate(self, attrs):
        errors = {}

        # منع النص الفارغ أو المسافات فقط
        if not attrs.get("title", "").strip():
            errors["title"] = "عنوان الفكرة مطلوب"

        if not attrs.get("skill_required", "").strip():
            errors["skill_required"] = "الرجاء اختيار مهارة واحدة على الأقل"

        if not attrs.get("description", "").strip():
            errors["description"] = "شرح الفكرة مطلوب"

        # عدد المتطوعين
        members_needed = attrs.get("members_needed")

        if members_needed is not None:
            if members_needed < 1 or members_needed > 3:
                errors["members_needed"] = (
                    "عدد المتطوعين يجب أن يكون بين 1 و 3 فقط"
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
        


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

class ExhibitionSubmissionCreateSerializer(
    serializers.Serializer
):
    data = serializers.JSONField()

    def validate(self, attrs):
        idea = self.context["idea"]
        request_user = (
            self.context["request"].user
        )

        if idea.owner_id != request_user.id:
            raise serializers.ValidationError(
                "Only the idea owner can submit exhibition form."
            )

        already_submitted = (
            ExhibitionSubmission.objects.filter(
                project=idea
            ).exists()
        )

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

        submitted_data = attrs["data"]

        # ==================================
        # IMAGE QUESTIONS VALIDATION
        # ==================================

        image_questions = (
            form.questions.filter(
                type=ExhibitionQuestion.IMAGE
            )
        )

        request = self.context["request"]

        for question in image_questions:

            uploaded_file = request.FILES.get(
                question.key
            )

            if (
                question.required
                and not uploaded_file
            ):
                raise serializers.ValidationError(
                    {
                        question.key:
                        "الصورة مطلوبة"
                    }
                )

        attrs["form"] = form
        return attrs


#///////////////////////// ExhibitionList > تاب المشاريع ////////////////////////
from django.conf import settings

class PublicExhibitionListSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    title = serializers.SerializerMethodField()
    sector = serializers.CharField(source="project.sector")
    team_members = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    def get_title(self, obj):
        return obj.project.title or ""

    def get_image(self, obj):
        image = (obj.data.get("صورة المشروع")
            or obj.data.get("project_image")
            or obj.data.get("logo")
            or obj.data.get("صورة المشروع")
            or obj.data.get("لوغو المشروع ")
            or obj.data.get("صورة-المشروع") 
            or obj.data.get("ارفع صورة لتكون واجهة المشروع"))
        

        if not image:
            return None

        request = self.context.get("request")

        image = f"{settings.MEDIA_URL}{image}"

        if request:
            return request.build_absolute_uri(image)

        return image

    def get_team_members(self, obj):
        return [
            member.user.full_name
            for member in obj.project.team_members.select_related("user")
        ]

    def get_owner(self, obj):
        return obj.project.owner.full_name
    
#/////////////////////////////// EXHIBITION DETAILS > عرض التفاصيل في تاب المشاريع /////////////

class PublicExhibitionDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    title = serializers.SerializerMethodField()
    sector = serializers.CharField(
        source="project.sector"
    )

    team_members = serializers.SerializerMethodField()

    project_goal = serializers.SerializerMethodField()

    project_services = serializers.SerializerMethodField()

    emails = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()

    owner_id = serializers.IntegerField(
        source="project.owner.id"
    )

    def get_title(self, obj):
        return (
            obj.data.get("title")
            or obj.project.title
        )
    def get_image(self, obj):
        print(obj.data)
        image = (
            obj.data.get("image")
            or obj.data.get("project_image")
            or obj.data.get("logo")
            or obj.data.get("صورة المشروع")
            or obj.data.get("لوغو المشروع ")
            or obj.data.get("صورة-المشروع") 
            or obj.data.get("ارفع صورة لتكون واجهة المشروع") 
        )
        if not image:
            return None
        image = str(image)
        if image.startswith("/media/"):
            return image
        return f"{settings.MEDIA_URL}{image}"

    def get_team_members(self, obj):
        return [
            member.user.full_name
            for member in obj.project.team_members.select_related(
                "user"
            )
        ]

    def get_project_goal(self, obj):
        return (
            obj.data.get("project_goal")
            or obj.data.get("goal")
            or obj.data.get("اهداف المشروع")
            or obj.data.get("اهداف-المشروع")
            or obj.data.get("هدف المشروع")
            or obj.data.get("الرؤية والهدف الاساسي")
            or obj.data.get("الرؤية-والهدف-الاساسي")
            or ""
        )

    def get_project_services(self, obj):
        return (
            obj.data.get("project_services")
            or obj.data.get("services")
            or obj.data.get("خدمات المشروع")
            or obj.data.get("خدمات-المشروع")
            or obj.data.get("المخرجات والخدمات التي يقدمها")
            or obj.data.get("المخرجات-والخدمات-التي-يقدمها")
            or ""
        )

    def get_emails(self, obj):
        return (
            obj.data.get("emails")
            or member.user.email
                for member in obj.project.team_members.select_related(
                "user"
            )
            or []
        )

    def get_owner_email(self, obj):
        return (
            obj.project.owner.email
            if obj.project.owner
            else ""
        )
    


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
        return (obj.answers.get("product_type")
                or obj.answers.get("نوع المنتج") )

    def get_phone(self, obj):
        return (obj.answers.get("phone")
                or obj.answers.get("رقم الهاتف")
                or obj.answers.get("الرقم")
                or obj.answers.get("رقم هاتف"))

    def get_specialization(self, obj):
        return (obj.answers.get("specialization")
                or obj.answers.get("الاختصاص"))

    def get_problem(self, obj):
        return (obj.answers.get("problem")
                or obj.answers.get("المشكلة")
                or obj.answers.get("مشكلة")
                or obj.answers.get("المشكلة التي يحلها المشروع")
                or obj.answers.get("المشكلة-التي-يحلها-المشروع")
                or obj.answers.get("المشكلة-التي-يحلها")
                or obj.answers.get("المشكلة التي يحلها"))
                            


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
    

class SeasonUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            "name",
            "description",
            "start_date",
            "end_date",
        ]

        extra_kwargs = {
            "name": {
                "error_messages": {
                    "required": "اسم الموسم مطلوب",
                    "blank": "اسم الموسم لا يمكن أن يكون فارغاً",
                }
            },
            "description": {
                "error_messages": {
                    "required": "وصف الموسم مطلوب",
                    "blank": "وصف الموسم لا يمكن أن يكون فارغاً",
                }
            },
            "start_date": {
                "error_messages": {
                    "required": "تاريخ بداية التقديم مطلوب",
                    "blank": "تاريخ بداية التقديم لا يمكن أن يكون فارغاً",
                    "null": "تاريخ بداية التقديم مطلوب",
                }
            },
            "end_date": {
                "error_messages": {
                    "required": "تاريخ انتهاء التقديم مطلوب",
                    "blank": "تاريخ انتهاء التقديم لا يمكن أن يكون فارغاً",
                    "null": "تاريخ انتهاء التقديم مطلوب",
                }
            },
        }

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                "end_date": "تاريخ انتهاء التقديم يجب أن يكون بعد تاريخ البداية"
            })

        return data
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

from ideas.models import (
    IdeaForm,
    FormStep,
    FormQuestion,
    FormQuestionChoice
)


# =====================================================
# CHOICES
# =====================================================

class FormChoicePayloadSerializer(
    serializers.Serializer
):

    id = serializers.IntegerField(
        required=False
    )

    value = serializers.CharField()

    label = serializers.CharField()

    order = serializers.IntegerField()


# =====================================================
# QUESTIONS
# =====================================================

class FormQuestionPayloadSerializer(
    serializers.Serializer
):

    id = serializers.IntegerField(
        required=False
    )

    # الجديد يلي شغال عليه السيرفيس
    is_static = serializers.BooleanField(
        default=False
    )

    # فقط للستاتيك
    static_field = serializers.ChoiceField(
        choices=[
            "title",
            "description",
            "target_audience",
            "sector"
        ],
        required=False,
        allow_null=True
    )

    # فقط للديناميك
    key = serializers.CharField(
        required=False
    )

    label = serializers.CharField(
        required=False
    )

    type = serializers.ChoiceField(
        choices=[
            "text",
            "number",
            "select",
            "boolean",
            "select_multiple",
            "list_text"
        ],
        required=False
    )

    required = serializers.BooleanField(
        default=False
    )

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

    # =================================================
    # VALIDATION
    # =================================================

    def validate(self, attrs):

        is_static = attrs.get(
            "is_static",
            False
        )

        # =============================================
        # STATIC QUESTION
        # =============================================

        if is_static:

            if not attrs.get(
                "static_field"
            ):
                raise serializers.ValidationError({
                    "static_field":
                    "هذا الحقل مطلوب"
                })

            # منع إرسال هالحقول
            attrs.pop("key", None)
            attrs.pop("label", None)
            attrs.pop("type", None)

        # =============================================
        # DYNAMIC QUESTION
        # =============================================

        else:

            required_fields = [
                "key",
                "label",
                "type"
            ]

            for field in required_fields:

                if not attrs.get(field):

                    raise serializers.ValidationError({
                        field:
                        "هذا الحقل مطلوب"
                    })

        return attrs


# =====================================================
# STEPS
# =====================================================

class FormStepPayloadSerializer(
    serializers.Serializer
):

    id = serializers.IntegerField(
        required=False
    )

    title = serializers.CharField()

    order = serializers.IntegerField()

    questions = FormQuestionPayloadSerializer(
        many=True
    )


# =====================================================
# ROOT
# =====================================================

class FormBuilderSerializer(
    serializers.Serializer
):

    title = serializers.CharField()

    steps = FormStepPayloadSerializer(
        many=True
    )


# =====================================================
# READ SERIALIZERS
# =====================================================

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


# =====================================================
# QUESTION READ
# =====================================================

class FormQuestionReadSerializer(
    serializers.ModelSerializer
):

    choices = FormChoiceReadSerializer(
        many=True,
        read_only=True
    )

    # يرجع للفرونت إذا السؤال static
    is_static = serializers.SerializerMethodField()

    class Meta:

        model = FormQuestion

        fields = [
            "id",
            "is_static",
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

    def get_is_static(self, obj):

        return (
            obj.source ==
            FormQuestion.STATIC
        )


# =====================================================
# STEP READ
# =====================================================

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


# =====================================================
# FORM READ
# =====================================================

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