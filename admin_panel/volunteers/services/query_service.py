from volunteers.models import VolunteerProfile

#\\\\\\\\\\\\\\\\\\\\\\\\\\عرض طلبات التطوع المعلقة\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
class VolunteerQueryService:

    @staticmethod
    def get_pending_volunteers():

        qs = VolunteerProfile.objects.filter(
            status=VolunteerProfile.PENDING
        ).select_related("user").prefetch_related("availabilities")

        data = []

        for v in qs:

            user = v.user

            # 🟢 الصورة (حل مشكلة None)
            avatar = None
            if hasattr(user, "avatar") and user.avatar:
                try:
                    avatar = user.avatar.url
                except:
                    avatar = None

            # 🟢 أوقات النشاط (نبسطها متل UI)
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

class VolunteerQueryService:

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

        return {
            "id": v.id,
            "name": user.full_name,
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
        }