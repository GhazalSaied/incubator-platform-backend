from django.core.exceptions import ValidationError
from evaluations.models import EvaluationCriterion
from .settings_service import SettingsService

class EvaluationCriteriaService:


    @staticmethod
    def ensure_not_published():
        settings = SettingsService.get()

        if settings.is_published:
            raise ValidationError(
                "لا يمكن تعديل المعايير بعد نشر النموذج"
            )
            
    @staticmethod
    def create(*, title, max_score):
        EvaluationCriteriaService.ensure_not_published()
        if EvaluationCriterion.objects.filter(title=title).exists():
            raise ValidationError("هذا المعيار موجود مسبقًا")

        return EvaluationCriterion.objects.create(
            title=title,
            max_score=max_score
        )

    # --------------------------------------

    @staticmethod
    def update(*, criteria, title=None, max_score=None):

        EvaluationCriteriaService.ensure_not_published()
        if title:
            if EvaluationCriterion.objects.exclude(id=criteria.id).filter(title=title).exists():
                raise ValidationError("اسم المعيار مستخدم")

            criteria.title = title

        if max_score:
            if max_score <= 0:
                raise ValidationError("الدرجة يجب أن تكون أكبر من صفر")

            criteria.max_score = max_score

        criteria.save()
        return criteria

    # --------------------------------------

    @staticmethod
    def delete_criteria(*, criteria):

        # منع الحذف بعد النشر
        EvaluationCriteriaService.ensure_not_published()

        criteria.delete()

        return True


    @staticmethod
    def get_active_criteria():
        return EvaluationCriterion.objects.filter(
            is_active=True
        ).order_by("id")
        
        


    @staticmethod
    def publish():

        settings = SettingsService.get()

        if settings.is_published:
            raise ValidationError("النموذج منشور بالفعل")

        criteria = EvaluationCriterion.objects.filter(is_active=True)

        if not criteria.exists():
            raise ValidationError("لا يوجد معايير للنشر")

        settings.is_published = True
        settings.save(update_fields=["is_published"])

        return settings