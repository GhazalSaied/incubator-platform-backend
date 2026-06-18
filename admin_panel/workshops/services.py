from rest_framework.exceptions import ValidationError
from django.db import transaction
from core.events import EventBus
from volunteers.models import Workshop


class WorkshopQueryService:

    STATUS_MAP = {
        "PENDING": "بانتظار الموافقة ",
        "ACCEPTED": "مقبول",
        "REJECTED": "مرفوض",
    }

    @staticmethod
    def list_workshops():

        workshops = Workshop.objects.select_related(
            "created_by"
        ).order_by("-created_at")

        data = []

        for workshop in workshops:

            data.append({
                "id": workshop.id,
                "title": workshop.title,
                "start_date": workshop.start_date,
                "volunteer_name": workshop.created_by.full_name,
                "status": WorkshopQueryService.STATUS_MAP.get(
                    workshop.status,
                    workshop.status
                )
            })

        return data
    

    @staticmethod
    def get_workshop_details(*, workshop_id,request=None):

        try:
            workshop = Workshop.objects.select_related(
                "created_by"
            ).get(id=workshop_id)

        except Workshop.DoesNotExist:
            raise ValidationError("الورشة غير موجودة")

        image = None

        if workshop.image:
            try:
                image = (
                request.build_absolute_uri(
                workshop.image.url
            )
                    if request
                    else workshop.image.url
        )
            except:
                image = None

        return {
            "id": workshop.id,
            "title": workshop.title,
            "category": workshop.category,
            "description": workshop.description,
            "objectives": workshop.objectives,
            "target_audience": workshop.target_audience,

            "start_date": workshop.start_date,
            "end_date": workshop.end_date,

            "days": workshop.days,

            "time_from": workshop.time_from,
            "time_to": workshop.time_to,

            "capacity": workshop.capacity,
            "sessions": workshop.sessions,

            "status": workshop.status,

            "rejection_reason": workshop.rejection_reason,

            "volunteer_name": workshop.created_by.full_name,

            "image": image
        }
        


from django.db import transaction
from django.core.exceptions import ValidationError


class WorkshopManagementService:

    @staticmethod
    @transaction.atomic
    def approve_workshop(*, workshop_id):

        try:
            workshop = Workshop.objects.select_related("created_by").get(id=workshop_id)
        except Workshop.DoesNotExist:
            raise ValidationError("الورشة غير موجودة")

        if workshop.status != "PENDING":
            raise ValidationError("لا يمكن قبول هذه الورشة")

        workshop.status = "ACCEPTED"
        workshop.rejection_reason = ""

        workshop.save(update_fields=["status", "rejection_reason"])

        EventBus.emit(
            "workshop_approved",
            workshop=workshop
        )

        return workshop

    @staticmethod
    @transaction.atomic
    def reject_workshop(*, workshop_id, rejection_reason):

        try:
            workshop = Workshop.objects.select_related("created_by").get(id=workshop_id)
        except Workshop.DoesNotExist:
            raise ValidationError("الورشة غير موجودة")

        if workshop.status != "PENDING":
            raise ValidationError("لا يمكن رفض هذه الورشة")

        if not rejection_reason or not rejection_reason.strip():
            raise ValidationError("سبب الرفض مطلوب")

        workshop.status = "REJECTED"
        workshop.rejection_reason = rejection_reason.strip()

        workshop.save(update_fields=["status", "rejection_reason"])

        transaction.on_commit(lambda: EventBus.emit(
            "workshop_rejected",
            workshop=workshop,
            rejection_reason=rejection_reason
        ))

        return workshop