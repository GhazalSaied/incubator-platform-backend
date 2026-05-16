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
        import notifications.handlers.season_handlers
        import notifications.handlers.bootcamp_handlers
        import notifications.handlers.admin_evaluation_handlers
        import notifications.handlers.admin_incubation_handlers
        import notifications.handlers.admin_exhibition_handlers
        import notifications.handlers.admin_volunteer_handlers
<<<<<<< Updated upstream
=======
        import notifications.handlers.manage_users
        import notifications.handlers.admin_broadcast
>>>>>>> Stashed changes
        