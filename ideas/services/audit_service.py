from ideas.models import IdeaAuditLog
from django.db import models


class AuditService:

    @staticmethod
    def log_status_change(idea, from_status, to_status, user=None):
        IdeaAuditLog.objects.create(
            idea=idea,
            from_status=from_status,
            to_status=to_status,
            performed_by=user
           
        )