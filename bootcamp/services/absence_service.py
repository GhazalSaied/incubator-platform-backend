from bootcamp.models import BootcampAbsenceRequest
from ideas.services.idea_service import IdeaService
from rest_framework.exceptions import ValidationError

class AbsenceService:

    @staticmethod
    def request_absence(user, session_id, reason):

        idea = IdeaService.get_user_idea(user)

        existing = BootcampAbsenceRequest.objects.filter(
            idea=idea,
            session_id=session_id
        ).exists()

        if existing:
            raise ValidationError("تم تقديم طلب غياب مسبقاً لهذه الجلسة")

        return BootcampAbsenceRequest.objects.create(
            idea=idea,
            session_id=session_id,
            reason=reason
        )