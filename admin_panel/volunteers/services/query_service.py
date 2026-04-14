from volunteers.models import VolunteerProfile
from evaluations.models import EvaluationInvitation
from django.core.exceptions import ValidationError
from django.utils import timezone

#\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع\المتطوعين   \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class VolunteerQueryService:

    @staticmethod
    def get_volunteers_by_status(*, status):

        qs = VolunteerProfile.objects.filter(
            status=status
        ).select_related("user").prefetch_related("availabilities")

        data = []

        for v in qs:

            user = v.user

            # 🟢 الصورة
            avatar = None
            if hasattr(user, "avatar") and user.avatar:
                try:
                    avatar = user.avatar.url
                except:
                    avatar = None

            # 🟢 أوقات النشاط
            times = []
            for a in v.availabilities.all():
                times.append(f"{a.start_time} - {a.end_time}")

            data.append({
                "id": v.id,
                "name": user.full_name,
                "avatar": avatar,
                "primary_skills": v.primary_skills,
                "availability": times
            })

        return data
    
#\\\\\\\\\\\\\\\\\\\\\\تفاصيل طلب التطوع \\\\\\\\\\\\\\\\\\\\\\\\\\\



    @staticmethod
    def get_volunteer_details(*, volunteer_id):

        try:
            v = VolunteerProfile.objects.select_related("user").prefetch_related("availabilities").get(id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            return None

        user = v.user

        # 🟢 الصورة
        avatar = None
        if hasattr(user, "avatar") and user.avatar:
            try:
                avatar = user.avatar.url
            except:
                avatar = None

        # 🟢 أوقات التفرغ
        availability = []
        for a in v.availabilities.all():
            availability.append({
                "day": a.day,
                "from": a.start_time,
                "to": a.end_time
            })
        has_accepted_invitation = EvaluationInvitation.objects.filter(
            user=v.user,
            status="ACCEPTED"
        ).exists()
 
        return {
            "id": v.id,
            "name": user.full_name,
            "status": v.status,#\\\\\\\\\\\\رح يرجع الحالة لما بتكون (pending) زر قبول ورفض اما لما تكون (approved) .زر ارسال طلب تقييم 
            "avatar": avatar,

            # 🟢 معلومات الخبرة
            "primary_skills": v.primary_skills,
            "years_of_experience": v.years_of_experience,
            "additional_skills": v.additional_skills,

            # 🟢 معلومات التطوع
            "volunteer_type": v.volunteer_type,
            "availability_type": v.availability_type,
            "motivation": v.motivation,

            # 🟢 الملف
            "cv": v.cv.url if v.cv else None,

            # 🟢 أوقات التفرغ
            "availability": availability,

            # 🟢 بيانات المستخدم
            "email": user.email,
            "is_evaluator": has_accepted_invitation,
            "status": v.status,
        }
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض  المقيمين  \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    @staticmethod
    def get_evaluators(*, season):

        invitations = EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED"
        ).select_related("user")

        user_ids = invitations.values_list("user_id", flat=True)

        volunteers = VolunteerProfile.objects.filter(
            user_id__in=user_ids
        ).select_related("user").prefetch_related("availabilities")

        data = []

        for v in volunteers:

            user = v.user

            # 🟢 الصورة
            avatar = None
            if hasattr(user, "avatar") and user.avatar:
                try:
                    avatar = user.avatar.url
                except:
                    avatar = None

            # 🟢 أوقات النشاط
            times = []
            for a in v.availabilities.all():
                times.append(f"{a.start_time} - {a.end_time}")

            data.append({
                "id": v.id,
                "name": user.full_name,
                "avatar": avatar,
                "primary_skills": v.primary_skills,
                "availability": times
            })

        return data