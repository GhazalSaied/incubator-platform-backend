from notifications.models import NotificationPreference


class PreferenceService:

    @staticmethod
    def is_enabled(user, event_name, role):

        pref = NotificationPreference.objects.filter(
            user=user,
            event_name=event_name,
            role=role
        ).first()

        # default = ON
        if not pref:
            return True

        return pref.is_enabled