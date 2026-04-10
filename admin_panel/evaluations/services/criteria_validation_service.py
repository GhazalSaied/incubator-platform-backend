from django.core.exceptions import ValidationError
from .settings_service import SettingsService


class CriteriaValidationService:

    @staticmethod
    def ensure_not_published():
        settings = SettingsService.get()

        if settings.is_published:
            raise ValidationError(
                "لا يمكن تعديل المعايير بعد نشر النموذج"
            )