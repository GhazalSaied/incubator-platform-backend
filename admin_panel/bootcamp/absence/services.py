from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from bootcamp.models import BootcampAbsenceRequest
from notifications.models import Notification


def get_absence_requests():
    return BootcampAbsenceRequest.objects.select_related(
        "idea", "session", "idea__owner"
    )


def process_absence_decision(request_id, decision):
    absence = get_object_or_404(BootcampAbsenceRequest, id=request_id)

    if absence.status != "pending":
        raise ValidationError("تم اتخاذ قرار مسبقاً")

    if decision == "approve":
        absence.status = "approved"

        Notification.objects.create(
            user=absence.idea.owner,
            title="طلب الغياب",
            message="تم قبول طلب الغياب الخاص بك ✅"
        )

    elif decision == "warn":
        absence.status = "warned"

        Notification.objects.create(
            user=absence.idea.owner,
            title="تحذير",
            message="تم رفض طلب الغياب ⚠️ يرجى الالتزام بالحضور"
        )

    else:
        raise ValidationError("قرار غير صالح")

    absence.save()
    return absence