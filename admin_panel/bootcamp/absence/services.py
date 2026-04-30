from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from django.db import transaction
from bootcamp.models import BootcampAbsenceRequest
from notifications.models import Notification
from core.events import EventBus
from django.db.models import Q


class AbsenceQueryService:

    @staticmethod
    def search(query=None):
        qs = BootcampAbsenceRequest.objects.select_related(
            "idea",
            "idea__owner"
        )

        if query:
            qs = qs.filter(
                Q(idea__title__icontains=query) |
                Q(idea__owner__full_name__icontains=query)
            )

        return qs.order_by("-id")
    
    @staticmethod
    def get_absence_requests():
        return BootcampAbsenceRequest.objects.select_related(
            "idea", "session", "idea__owner"
        )



@transaction.atomic
def process_absence_decision(request_id, decision, actor=None):

    absence = get_object_or_404(BootcampAbsenceRequest, id=request_id)

    if absence.status != "pending":
        raise ValidationError("تم اتخاذ قرار مسبقاً")

    if decision == "approve":
        absence.status = "approved"

    elif decision == "warn":
        absence.status = "warned"

    else:
        raise ValidationError("قرار غير صالح")

    absence.save(update_fields=["status"])

    # 🔥 EventBus بدل Notification مباشر
    EventBus.emit(
        "absence_decision_made",
        absence=absence,
        decision=absence.status,
        idea=absence.idea,
        actor=actor
    )

    return absence