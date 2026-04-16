# notifications/apps.py

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        import notifications.handlers.consultation_handlers
        import notifications.handlers.team_handlers
        import notifications.handlers.workshop_handlers
        import notifications.handlers.evaluation_handlers
        import notifications.handlers.messaging_handlers
        import notifications.handlers.system_handlers