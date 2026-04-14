from urllib import request
from datetime import datetime
from django.utils import timezone
from dateutil import parser
from django.core.exceptions import ValidationError
from django.db import transaction
from ideas.models import Season
from volunteers.models import VolunteerProfile
from django.utils import timezone
from ideas.services.season_phase_service import SeasonPhaseService
from evaluations.models import EvaluationInvitation


class VolunteerManagementService:

    @staticmethod
    @transaction.atomic
    def approve_volunteer(*, volunteer_id):

        try:
            v = VolunteerProfile.objects.select_related("user").get(id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            raise ValidationError("المتطوع غير موجود")

        # 🛑 تحقق الحالة
        if v.status != VolunteerProfile.PENDING:
            raise ValidationError("لا يمكن قبول هذا الطلب")

        v.status = VolunteerProfile.APPROVED
        v.save(update_fields=["status"])

        return v

    # ----------------------------------------

    @staticmethod
    @transaction.atomic
    def reject_volunteer(*, volunteer_id):

        try:
            v = VolunteerProfile.objects.select_related("user").get(id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            raise ValidationError("المتطوع غير موجود")

        # 🛑 تحقق الحالة
        if v.status != VolunteerProfile.PENDING:
            raise ValidationError("لا يمكن رفض هذا الطلب")

        v.status = VolunteerProfile.REJECTED
        v.save(update_fields=["status"])

        return v
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ازالة مقيم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    @staticmethod
    @transaction.atomic
    def remove_evaluator_role(*, volunteer_id):
        
        # 🛑 تحقق المتطوع
        try:
            volunteer = VolunteerProfile.objects.select_related("user").get(id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            raise ValidationError("المتطوع غير موجود")

        # 🛑 جيب الدعوة المقبولة فقط
        invitation = EvaluationInvitation.objects.filter(
            user=volunteer.user,
            status="ACCEPTED"
        ).select_for_update().first()

        # 🛑 إذا مو مقيم
        if not invitation:
            raise ValidationError("هذا المستخدم ليس مقيم حالياً")

        # 🟢 تحديث الحالة (Soft remove)
        invitation.status = "REVOKED"
        invitation.responded_at = timezone.now()
        invitation.save(update_fields=["status", "responded_at"])

        return {
            "success": True,
            "volunteer_id": volunteer.id
        }
    
    
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\إرسال دعوة تقييم \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    @staticmethod
    @transaction.atomic
    def send_invitation_to_volunteer(
        *,
        volunteer_id,
        description,
        meeting_date,
        expected_duration,
        task,
        expertise_field
    ):
        season = SeasonPhaseService.get_current_season()


        # 🛑 تحقق الموسم
        try:
            season = Season.objects.get(id=season.id)
        except Season.DoesNotExist:
            raise ValidationError("الموسم غير موجود")

        # 🛑 تحقق المتطوع
        try:
            v = VolunteerProfile.objects.select_related("user").get(id=volunteer_id)
        except VolunteerProfile.DoesNotExist:
            raise ValidationError("المتطوع غير موجود")

        # 🛑 لازم يكون مقبول
        if v.status != VolunteerProfile.APPROVED:
            raise ValidationError("لا يمكن إرسال دعوة لهذا المتطوع")

        # 🟢 تحويل التاريخ
        try:
            meeting_date = datetime.strptime(
                meeting_date,
                "%Y-%m-%d %H:%M"
            )
            meeting_date = timezone.make_aware(meeting_date)
        except Exception:
            raise ValidationError("تنسيق التاريخ غير صحيح")

        # 🛑 تحقق التاريخ
        if meeting_date < timezone.now():
            raise ValidationError("لا يمكن تحديد موعد في الماضي")

        # 🛑 منع التكرار (smart)
        exists = EvaluationInvitation.objects.filter(
            user=v.user,
            season=season,
            status__in=["PENDING", "ACCEPTED"]
        ).exists()

        if exists:
            raise ValidationError("هذا المتطوع لديه دعوة فعالة بالفعل")

        # 🟢 إنشاء الدعوة
        invitation = EvaluationInvitation.objects.create(
            user=v.user,
            season=season,
            description=description,
            meeting_date=meeting_date,
            expected_duration=expected_duration,
            task=task,
            expertise_field=expertise_field
        )

        return invitation