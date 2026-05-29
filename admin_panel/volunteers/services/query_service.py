from accounts.constants import SystemRoles
from accounts.models import UserRole
from ideas.models import TeamRequest
import volunteers
from volunteers.models import VolunteerProfile
from evaluations.models import EvaluationInvitation
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import F
#\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع\المتطوعين   \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class VolunteerQueryService:

    @staticmethod
    def get_volunteers_by_status(*, status,specialization=None):

        qs = VolunteerProfile.objects.filter(
            status=status
        ).select_related("user").prefetch_related("availabilities")
        if specialization:
            qs = qs.filter(specialization=specialization)
        data = []

        for v in qs:

            user = v.user

            avatar = None
            if hasattr(user, "avatar") and user.avatar:
                try:
                    avatar = user.avatar.url
                except:
                    avatar = None

            times = []
            for a in v.availabilities.all():
                times.append(f"{a.day}: {a.start_time.strftime("%H:%M")} - {a.end_time.strftime("%H:%M")}")

            data.append({
                "id": v.id,
                "name": user.full_name,
                "avatar": avatar,
                "specialization": v.specialization,
                "availability": times,
                "status": v.status
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

        avatar = None
        if hasattr(user, "avatar") and user.avatar:
            try:
                avatar = user.avatar.url
            except:
                avatar = None

        availability = []
        for a in v.availabilities.all():
            availability.append({
                "day": a.day,
                "from": a.start_time.strftime("%H:%M"),
                "to": a.end_time.strftime("%H:%M")
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

            #  معلومات الخبرة
            "primary_skills": v.primary_skills,
            "years_of_experience": v.years_of_experience,
            "additional_skills": v.additional_skills,
            "specialization": v.specialization,
            "current_company": v.current_company,

            #  معلومات التطوع
            "volunteer_type": v.volunteer_type,
            "availability_type": v.availability_type,
            "motivation": v.motivation,

            #  أوقات التفرغ
            "availability": availability,
            "bio": v.bio,
            "residence": v.residence,

            #  بيانات المستخدم
            "email": user.email,
            "is_evaluator": has_accepted_invitation,
            "roles": [r.role.code for r in user.userrole_set.filter(is_active=True)],
            "user_id": user.id,
            
        }
        
        
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\عرض  المقيمين  \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    @staticmethod
    def get_evaluators(*, season):

       #  1. evaluators من الدعوات المقبولة
        invited_user_ids = EvaluationInvitation.objects.filter(
            season=season,
            status="ACCEPTED"
        ).values_list("user_id", flat=True)

    #  2. evaluators من roles
        role_user_ids = UserRole.objects.filter(
            role__code=SystemRoles.EVALUATOR,
            is_active=True
        ).values_list("user_id", flat=True)

    #  3. دمج الاثنين
        all_user_ids = set(invited_user_ids) | set(role_user_ids)

    #  4. جلب volunteer profiles
        volunteers = VolunteerProfile.objects.filter(
            user_id__in=all_user_ids
        ).select_related("user").prefetch_related("availabilities")

        data = []

        for v in volunteers:

            user = v.user

        #  الصورة
            avatar = None
            if user.avatar:
                try:
                    avatar = user.avatar.url
                except:
                    avatar = None

        #  أوقات النشاط
            times = [
                f"{a.start_time} - {a.end_time}"
                for a in v.availabilities.all()
            ]

            data.append({
                "id": v.id,
                "name": user.full_name,
                "avatar": avatar,
                "specialization": v.specialization,
                "availability": times
            })

        return data
    
    
        
    @staticmethod
    def get_idea_owners_with_team_requests(season=None):

        qs = TeamRequest.objects.filter(
        status="PENDING"
        ).select_related("idea__owner")

        if season:
            qs = qs.filter(idea__season=season)

        qs = qs.values(
            user_id=F("idea__owner__id"),
            name=F("idea__owner__full_name"),
            avatar=F("idea__owner__avatar")
        ).distinct()

        data = []

        for item in qs:
            avatar = item["avatar"]
            avatar_url = avatar.url if avatar else None

            data.append({
                "id": item["user_id"],
                "name": item["name"],
                "avatar": avatar_url
            })

        return data




    @staticmethod
    def get_team_request_details(request_id):

        tr = TeamRequest.objects.select_related(
        "idea"
        ).filter(id=request_id).first()

    # fallback للفرونت الحالي (user id)
        if not tr:
            tr = TeamRequest.objects.select_related(
            "idea"
            ).filter(
            idea__owner_id=request_id
            ).first()

        if not tr:
            raise ValidationError("الطلب غير موجود")

        return {
            "id": tr.id,
            "title": tr.title,
            "skill_required": tr.skill_required,
            "members_needed": tr.members_needed,
            "description": tr.description,
            "idea": {
            "idea_id": tr.idea.id,
        }
    }

    @staticmethod
    def get_available_approved_volunteers():

        volunteers = VolunteerProfile.objects.filter(
            status="APPROVED"
        ).exclude(
            user__userrole__role__code__in=[
                SystemRoles.IDEA_OWNER,
                SystemRoles.INCUBATOR
            ],
            user__userrole__is_active=True
        ).select_related("user").distinct()
        data = []
        for v in volunteers :
            user = v.user
            avatar = None
            if hasattr(user, "avatar") and user.avatar:
                try:
                    avatar = user.avatar.url
                except:
                    avatar = None
            times = []
            for a in v.availabilities.all():
                times.append(f"{a.day}: {a.start_time} - {a.end_time}")

            data.append({
                "id": v.id,
                "name": user.full_name,
                "avatar": avatar,
                "specialization": v.specialization,
                "availability": times
            })

        return data