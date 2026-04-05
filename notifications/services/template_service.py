from notifications.models import NotificationTemplate
from django.core.exceptions import ObjectDoesNotExist


class TemplateService:

    @staticmethod
    def render(code: str, context: dict):

        try:
            template = NotificationTemplate.objects.get(code=code, is_active=True)
        except ObjectDoesNotExist:
            return "Notification", "No message"

        message = template.message
        title = template.title

        for key, value in context.items():
            message = message.replace(f"{{{{ {key} }}}}", str(value))
            title = title.replace(f"{{{{ {key} }}}}", str(value))

        return title, message