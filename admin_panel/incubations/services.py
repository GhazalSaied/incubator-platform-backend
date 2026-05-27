
from datetime import datetime, timedelta
from core.events import EventBus
from evaluations.models import EvaluationInvitation
from django.utils import timezone
from ideas.models import Idea, IdeaStatus
from django.core.exceptions import ValidationError
from evaluations.models import IncubationAssignment,IncubationReview
from notifications.services.notification_service import NotificationService
from volunteers.models import VolunteerProfile
from django.db import transaction
from django.db.models import Max
#\\\\\\\\\\\\\\\\\\\\\\\\\\ لوحة تحكم المشاريع المحتضنة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class IncubationDashboardService:

    @staticmethod
    def get_projects():

        ideas = Idea.objects.filter(
            status=IdeaStatus.INCUBATION
        ).select_related("owner")

        data = []
        now = timezone.now()

        for idea in ideas:

            # =========================
            # 1. LAST MEETING DATE
            # =========================

            last_meeting_date = IncubationReview.objects.filter(
                idea=idea
            ).aggregate(
                last_date=Max("submitted_at")
            )["last_date"]

            # =========================
            # 2. REVIEWS OF LAST MEETING ONLY
            # =========================

            last_reviews = IncubationReview.objects.filter(
                idea=idea,
                submitted_at=last_meeting_date
            )

            # =========================
            # 3. AVERAGE PROGRESS SCORE
            # =========================

            scores = [
                r.progress_score
                for r in last_reviews
                if r.progress_score is not None
            ]

            avg_score = (
                sum(scores) / len(scores)
                if scores else 0
            )

            # =========================
            # 4. STATUS CALCULATION
            # =========================
            status = "غير محدد"
            if avg_score < 25:
                status = "ضعيف"
            elif avg_score < 50:
                status = "متوسط"
            elif avg_score < 75:
                status = "جيد"
            else:
                status = "ممتاز"

            # =========================
            # 5. NEXT MEETING
            # =========================

            next_meeting = IncubationAssignment.objects.filter(
                idea=idea,
                meeting_date__gt=now
            ).order_by("meeting_date").first()

            # =========================
            # RESULT
            # =========================

            data.append({
                "idea_id": idea.id,
                "title": idea.title,

                # next meeting
                "next_meeting": (
                    next_meeting.meeting_date.strftime("%d/%m/%Y")
                    if next_meeting else "لم يتم تحديد موعد"
                ),

                # computed status
                "progress_status": status if scores else "غير مقيم"
            })

        return data
 #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض المقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\    
class IncubationQueryService:

    @staticmethod
    def get_idea_mentors(*, idea):

        assignments = idea.incubation_assignments.select_related(
            "mentor",
            "mentor__user"
        )

        data = []

        for a in assignments:
            profile = a.mentor
            user = profile.user

            data.append({
                "id": profile.id,
                "name": user.full_name,
                "image": user.avatar.url if user.avatar else None,
                "specialization": profile.specialization,
            })

        return data

    @staticmethod
    def get_available_evaluators(*, season, specialization=None, fields=None):

        qs = EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED"
        ).select_related("user", "user__volunteer_profile")

        #  فلترة الاختصاص
        if specialization:
            qs = qs.filter(
                user__volunteer_profile__specialization__icontains=specialization
            )

        #  فلترة المجالات
        if fields:
            qs = qs.filter(
                user__volunteer_profile__primary_skills__icontains=fields
            )

        return qs
    @staticmethod
    def get_available_evaluators_data(*, season, specialization=None, fields=None):

        invitations = IncubationQueryService.get_available_evaluators(
            season=season,
            specialization=specialization,
            fields=fields
        )


        data = []

        for inv in invitations:
            user = inv.user
            profile = user.volunteer_profile
            print("AVAILABLE EVALUATORS SEASON:", season)

            print(
            "AVAILABLE USERS:",
            list(
                inv.values_list("user_id", flat=True)
             )
           )
            data.append({
                "user_id": user.id,
                "name": user.full_name,
                "specialization": profile.specialization,
                "fields": profile.primary_skills,
            })

        return data
    
    


#\\\\\\\\\\\\حذف مقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\

class IncubationAssignmentService:

    @staticmethod
    @transaction.atomic
    def remove_mentors(*, idea, mentor_ids):

        #  تحقق من الإدخال
        if not mentor_ids:
            raise ValidationError("يجب اختيار مقيم واحد على الأقل")

      
        #  جلب العلاقات الموجودة فقط
        existing_assignments = IncubationAssignment.objects.filter(
            idea=idea,
            mentor_id__in=mentor_ids
        )

        if not existing_assignments.exists():
            raise ValidationError("المقيمون غير مرتبطين بهذه الفكرة")

        #  حذف
        deleted_count, _ = existing_assignments.delete()

        return {
            "deleted_count": deleted_count
        }



    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تعيين مقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    @staticmethod
    @transaction.atomic
    def assign_mentors(*, idea, mentor_user_ids, season):

        #  1. تحقق من الإدخال
        if not mentor_user_ids:
            raise ValidationError("يجب اختيار مقيم واحد على الأقل")

        #  3. جلب الدعوات المقبولة فقط
        invitations = EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED",
            user_id__in=mentor_user_ids
        ).select_related("user", "user__volunteer_profile")
        print("season:", season)
        print("mentor_user_ids:", mentor_user_ids)

        print(
           "ALL ACCEPTED USERS:",
        list(
           EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED"
        ).values_list("user_id", flat=True)
    )
)

        print(
            "MATCHED:",
        list(invitations.values_list("user_id", flat=True))
        )
        if not invitations.exists():
            raise ValidationError("لا يوجد مقيمون مقبولون بهذه المعطيات")

        assigned = []
        skipped = []

        for inv in invitations:

            user = inv.user

            #  4. منع صاحب الفكرة
            if user.id == idea.owner_id:
                skipped.append({
                    "user_id": user.id,
                    "reason": "OWNER_CANNOT_BE_MENTOR"
                })
                continue

            profile = getattr(user, "volunteer_profile", None)

            if not profile:
                skipped.append({
                    "user_id": user.id,
                    "reason": "NO_PROFILE"
                })
                continue

            #  5. منع التكرار
            exists = IncubationAssignment.objects.filter(
                idea=idea,
                mentor=profile
            ).exists()

            if exists:
                skipped.append({
                    "user_id": user.id,
                    "reason": "ALREADY_ASSIGNED"
                })
                continue

            #  6. إنشاء العلاقة
            assignment = IncubationAssignment.objects.create(
                idea=idea,
                mentor=profile
            )

            assigned.append(assignment)

        return {
            "assigned_count": len(assigned),
            "skipped": skipped
        }
        
        

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\جدولة جلسة متابعة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



class IncubationMeetingService:

    DEFAULT_DURATION = timedelta(hours=1)

    @staticmethod
    @transaction.atomic
    def schedule_meeting(*, idea, date, time, created_by):

        # =========================
        # VALIDATION
        # =========================

        if not date or not time:
            raise ValidationError(
                "التاريخ والوقت مطلوبان"
            )

        try:
            meeting_datetime = datetime.strptime(
                f"{date} {time}",
                "%Y-%m-%d %H:%M"
            )

        except ValueError:
            raise ValidationError(
                "تنسيق التاريخ غير صحيح"
            )

        meeting_datetime = timezone.make_aware(
            meeting_datetime
        )

        if meeting_datetime <= timezone.now():
            raise ValidationError(
                "لا يمكن تحديد موعد في الماضي"
            )

        # =========================
        # ASSIGNMENTS
        # =========================

        assignments = (
            IncubationAssignment.objects
            .select_related("mentor")
            .filter(idea=idea)
        )

        if not assignments.exists():
            raise ValidationError(
                "لا يوجد mentors مرتبطون"
            )

        # =========================
        # CONFLICT CHECK
        # =========================

        duration = (
            IncubationMeetingService.DEFAULT_DURATION
        )

        new_start = meeting_datetime
        new_end = meeting_datetime + duration

        conflict = (
            IncubationAssignment.objects.filter(
                meeting_date__lt=new_end,
                meeting_date__gte=new_start
            )
            .exclude(idea=idea)
            .exists()
        )

        if conflict:
            raise ValidationError(
                "يوجد لجنة أخرى بنفس الساعة"
            )

        # =========================
        # UPDATE MEETING DATE
        # =========================

        assignments.update(
            meeting_date=meeting_datetime
        )

        # refresh objects
        assignments = list(
            IncubationAssignment.objects.select_related(
                "mentor"
            ).filter(idea=idea)
        )

        # =========================
        # EVENT
        # =========================

        EventBus.emit(
            "incubation_meeting_scheduled",
            idea=idea,
            meeting_date=meeting_datetime,
            assignments=assignments,
            actor=created_by
        )

        return assignments
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض ملاحظات ىاخر جلسة\\\\\\\\\\\\\\\\\\\\\\\\\


class IncubationNotesService:

    @staticmethod
    def get_latest_review_notes(*, idea):

        now = timezone.now()

        # =====================================
        # أحدث مراجعة
        # =====================================

        latest_review = (
            IncubationReview.objects.filter(
                idea=idea,
                is_submitted=True,
                submitted_at__lte=now
            )
            .order_by("-submitted_at")
            .first()
        )

        if not latest_review:
            return {
                "meeting_date": None,
                "reviews": []
            }

        latest_date = latest_review.submitted_at.date()

        # =====================================
        # كل مراجعات نفس اليوم
        # =====================================

        reviews = (
            IncubationReview.objects
            .select_related("created_by", "idea")
            .filter(
                idea=idea,
                is_submitted=True,
                submitted_at__date=latest_date
            )
            .order_by("submitted_at")
        )

        data = []

        for review in reviews:

            mentor = review.created_by.volunteer_profile
            user = review.created_by

            avatar = None

            if hasattr(user, "avatar") and user.avatar:
                try:
                    avatar = user.avatar.url
                except Exception:
                    avatar = None

            data.append({
                "mentor_id": mentor.id,

                "mentor_name": (
                    getattr(user, "full_name", None)
                    or getattr(user, "username", "")
                ),

                "specialization": getattr(
                    mentor,
                    "specialization",
                    None
                ),

                "avatar": avatar,

                "notes": review.notes,
            })

        return {
            "meeting_date": latest_date.strftime("%d/%m/%Y"),
            "reviews": data
            
        }
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تخريج الفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
from django.db import transaction
from rest_framework.exceptions import ValidationError

from ideas.models import IdeaStatus
from ideas.services.state.idea_state_service import (
    IdeaStateService
)

from core.events import EventBus


class GraduationService:

    # ==========================================
    # POSITIVE GRADUATION
    # ==========================================

    @staticmethod
    @transaction.atomic
    def graduate_positive(*, idea, actor=None):

        # ----------------------------------
        # VALIDATION
        # ---------------------------------
            

        # لازم يكون في مراجعات احتضان
        if not idea.reviews.exists():
            raise ValidationError(
                "لا يمكن التخريج الإيجابي بدون مراجعات"
            )

        # ----------------------------------
        # STATE TRANSITION
        # ----------------------------------

        IdeaStateService.change_status(
            idea=idea,
            to_status=IdeaStatus.EXHIBITION,
            user=actor,
            source="EXHIBITION_GRADUATION"
        )

        # ----------------------------------
        # EVENT
        # ----------------------------------

        EventBus.emit("idea_exhibition_graduated",idea=idea,actor=actor)

        return idea

    # ==========================================
    # NEGATIVE GRADUATION
    # ==========================================

    @staticmethod
    @transaction.atomic
    def graduate_negative(*, idea, actor=None):

        # ----------------------------------
        # STATE TRANSITION
        # ----------------------------------

        IdeaStateService.change_status(
            idea=idea,
            to_status=IdeaStatus.GRADUATED_NEGATIVE,
            user=actor,
            source="graduation_negative"
        )

        # ----------------------------------
        # EVENT
        # ----------------------------------

        EventBus.emit(
            "idea_graduated_negative",
            idea=idea,
            actor=actor
        )

        return idea
    

from ideas.models import Idea, IdeaStatus


class GraduationQueryService:

    @staticmethod
    def list_negative_graduated_projects(
        search=None,
        category=None
    ):

        ideas = (
            Idea.objects
            .filter(
                status=IdeaStatus.GRADUATED_NEGATIVE
            )
            .select_related("owner")
            .prefetch_related("team_members")
        )

        # SEARCH
        if search:
            ideas = ideas.filter(
                title__icontains=search
            )

        # FILTER
        if category:
            ideas = ideas.filter(
                sector__iexact=category
            )

        data = []

        for idea in ideas:

            members = [
                member.user.full_name
                for member in idea.team_members.all()
            ]

            data.append({
                "id": idea.id,
                "title": idea.title,

                "team_members": members,

                "category": idea.sector,

                "status": idea.status,
                "year": idea.season.start_date.year,
            })

        return data