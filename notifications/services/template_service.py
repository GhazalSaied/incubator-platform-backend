from notifications.models import NotificationTemplate


class TemplateService:

    @staticmethod
    def render(code: str, context: dict):

        template = NotificationTemplate.objects.get(code=code)

        message = template.message
        title = template.title

        for key, value in context.items():
            message = message.replace(f"{{{{ {key} }}}}", str(value))
            title = title.replace(f"{{{{ {key} }}}}", str(value))

        return title, message