from django.db.models import Q
from django.utils import timezone

from accounts.models import User


def get_admin_user():

    now = timezone.now()

    return (
        User.objects
        .filter(
            is_active=True,
            userrole__role__code="ADMIN",
            userrole__is_active=True,
        )
        .filter(
            Q(userrole__expires_at__isnull=True)
            |
            Q(userrole__expires_at__gt=now)
        )
        .distinct()
        .first()
    )