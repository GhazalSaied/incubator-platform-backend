
from datetime import datetime, timedelta


from django.utils import timezone
from ideas.models import Idea, IdeaStatus
from django.core.exceptions import ValidationError
from evaluations.models import IncubationAssignment,IncubationReview
from notifications.services.notification_service import NotificationService
from volunteers.models import VolunteerProfile
from django.db import transaction

#\\\\\\\\\\\\\\\\\\\\\\\\\\ لوحة تحكم المشاريع المحتضنة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class IncubationDashboardService:

    @staticmethod
    def get_projects():

        ideas = Idea.objects.filter(
            status=IdeaStatus.INCUBATION
        )

        data = []

        now = timezone.now()

        for idea in ideas:

            # 🟢 كل المراجعات
            reviews = idea.reviews.all()

            # 🟢 آخر تقييم (للحالة)
            last_review = reviews.order_by("-meeting_date").first()

            # 🟢 التقييم القادم
            next_review = reviews.filter(
                meeting_date__gt=now
            ).order_by("meeting_date").first()

            # 🟢 تحديد الحالة
            status = "غير محدد"

            if last_review and last_review.progress_score is not None:
                score = last_review.progress_score

                if score < 25.00:
                    status = "ضعيف"
                elif score < 50.00:
                    status = "متوسط"
                else:
                    status = "جيد"

            data.append({
                "idea_id": idea.id,
                "title": idea.title,
                "next_meeting": next_review.meeting_date if next_review else None,
                "status": status,
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
                "specialization": profile.primary_skills,
            })

        return data
    


#\\\\\\\\\\\\حذف مقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\

class IncubationAssignmentService:

    @staticmethod
    @transaction.atomic
    def remove_mentors(*, idea, mentor_ids):

        # 🛑 تحقق من الإدخال
        if not mentor_ids:
            raise ValidationError("يجب اختيار مقيم واحد على الأقل")

        # 🛑 تحقق من مرحلة الفكرة
        if idea.status != IdeaStatus.INCUBATION:
            raise ValidationError("لا يمكن التعديل خارج مرحلة الاحتضان")

        # 🟢 جلب العلاقات الموجودة فقط
        existing_assignments = IncubationAssignment.objects.filter(
            idea=idea,
            mentor_id__in=mentor_ids
        )

        if not existing_assignments.exists():
            raise ValidationError("المقيمون غير مرتبطين بهذه الفكرة")

        # 🟢 حذف
        deleted_count, _ = existing_assignments.delete()

        return {
            "deleted_count": deleted_count
        }
        
        
from evaluations.models import EvaluationInvitation



class IncubationQueryService:

    @staticmethod
    def get_available_evaluators(*, season, specialization=None, fields=None):

        qs = EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED"
        ).select_related("user", "user__volunteer_profile")

        # 🟢 فلترة الاختصاص
        if specialization:
            qs = qs.filter(
                user__volunteer_profile__primary_skills__icontains=specialization
            )

        # 🟢 فلترة المجالات
        if fields:
            qs = qs.filter(
                user__volunteer_profile__additional_skills__icontains=fields
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

            data.append({
                "user_id": user.id,
                "name": user.full_name,
                "specialization": profile.primary_skills,
                "fields": profile.additional_skills,
            })

        return data
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تعيين مقيمين للفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class IncubationAssignmentService:

    @staticmethod
    @transaction.atomic
    def assign_mentors(*, idea, mentor_user_ids, season):

        # 🛑 1. تحقق من الإدخال
        if not mentor_user_ids:
            raise ValidationError("يجب اختيار مقيم واحد على الأقل")

        # 🛑 2. تحقق من المرحلة
        if idea.status != IdeaStatus.INCUBATION:
            raise ValidationError("لا يمكن التعيين خارج مرحلة الاحتضان")

        # 🟢 3. جلب الدعوات المقبولة فقط
        invitations = EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED",
            user_id__in=mentor_user_ids
        ).select_related("user", "user__volunteer_profile")

        if not invitations.exists():
            raise ValidationError("لا يوجد مقيمون مقبولون بهذه المعطيات")

        assigned = []
        skipped = []

        for inv in invitations:

            user = inv.user

            # 🛑 4. منع صاحب الفكرة
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

            # 🛑 5. منع التكرار
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

            # 🟢 6. إنشاء العلاقة
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

from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction


class IncubationMeetingService:

    DEFAULT_DURATION = timedelta(hours=1)

    @staticmethod
    @transaction.atomic
    def schedule_meeting(*, idea, date, time, created_by):

        # 🟢 Validation
        if not date or not time:
            raise ValidationError("التاريخ والوقت مطلوبان")

        try:
            meeting_datetime = datetime.strptime(
                f"{date} {time}",
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            raise ValidationError("تنسيق غير صحيح")

        # 🟢 تحويل لـ timezone aware
        meeting_datetime = timezone.make_aware(meeting_datetime)

        # 🟢 منع الماضي
        if meeting_datetime <= timezone.now():
            raise ValidationError("لا يمكن تحديد موعد في الماضي")

        duration = IncubationMeetingService.DEFAULT_DURATION

        new_start = meeting_datetime
        new_end = meeting_datetime + duration

        # 🟢 تحقق التداخل (مهم جداً: حسب نفس الفكرة فقط)
        conflict = IncubationReview.objects.filter(
            idea=idea,
            meeting_date__lt=new_end,
            meeting_date__gte=new_start
        ).exists()

        if conflict:
            raise ValidationError("يوجد جلسة متداخلة خلال هذه الساعة")

        # 🟢 تحقق وجود mentors
        assignments = IncubationAssignment.objects.filter(idea=idea)

        if not assignments.exists():
            raise ValidationError("لا يوجد مقيمون مرتبطون")

        # 🟢 إنشاء Review
        review = IncubationReview.objects.create(
            idea=idea,
            meeting_date=meeting_datetime,
            created_by=created_by
        )

        # 🟢 إشعار صاحب الفكرة
        NotificationService.send(
            user=idea.owner,
            title="تم تحديد جلسة متابعة 📅",
            message=f"موعد الجلسة: {meeting_datetime}",
            action_type="VIEW_IDEA",
            action_url="/ideas/my/",
            related_object=idea
        )

        # 🟢 إشعار المقيمين (optimized query)
        assignments = assignments.select_related("mentor__user")

        for a in assignments:
            NotificationService.send(
                user=a.mentor.user,
                title="جلسة متابعة جديدة",
                message=f"جلسة لفكرة {idea.title} بتاريخ {meeting_datetime}",
                action_type="VIEW_IDEA",
                action_url="/ideas/assigned/",
                related_object=idea
            )

        return review
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض ملاحظات ىاخر جلسة\\\\\\\\\\\\\\\\\\\\\\\\\


class IncubationNotesService:

    @staticmethod
    def get_latest_review_notes(*, idea):

        now = timezone.now()

        review = IncubationReview.objects.filter(
            idea=idea,
            meeting_date__lte=now
        ).order_by("-meeting_date").first()

        if not review:
            return {
                "review": None,
                "mentors": []
            }

        assignments = IncubationAssignment.objects.select_related(
            "mentor__user"
        ).filter(idea=idea)

        mentors = []

        for a in assignments:
            user = a.mentor.user
            profile = a.mentor

            avatar = None
            if hasattr(user, "avatar") and user.avatar:
                try:
                    avatar = user.avatar.url
                except Exception:
                    avatar = None

            mentors.append({
                "id": user.id,
                "name": user.full_name,
                "specialization": profile.primary_skills,
                "avatar": avatar
            })

        return {
            "review": {
                "meeting_date": review.meeting_date,
                "notes": review.notes,
                "progress_score": review.progress_score
            },
            "mentors": mentors
        }
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\تخريج الفكرة \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class GraduationService:

    @staticmethod
    def graduate_positive(*, idea):
        

        # ❗ لازم تكون ضمن الاحتضان
        if idea.status != IdeaStatus.INCUBATION:
            raise ValidationError("لا يمكن تخريج الفكرة")

        # ❗ لازم يكون في تقييمات
        if not idea.reviews.exists():
            raise ValidationError("لا يمكن التخريج الإيجابي بدون تقييمات")

        idea.status = IdeaStatus.GRADUATED_POSITIVE
        idea.save(update_fields=["status"])

        return idea
    
    @staticmethod
    def graduate_negative(*, idea):

        if idea.status != IdeaStatus.INCUBATION:
            raise ValidationError("لا يمكن تخريج الفكرة")

        idea.status = IdeaStatus.GRADUATED_NEGATIVE
        idea.save(update_fields=["status"])

        return idea
