from django.core.exceptions import ValidationError
from django.db import transaction

from volunteers.models import VolunteerProfile


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