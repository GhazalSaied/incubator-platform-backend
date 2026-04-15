from accounts.models import User
from django.db.models import Q

def get_users(role_code=None):
    qs = User.objects.all().order_by("-created_at")

    # 🛑 استثناء الإدارة (Director + Secretary)
    qs = qs.exclude(
        Q(groups__name="incubator directors") 
    )

    if role_code:
        qs = qs.filter(
            userrole__role__code=role_code,
            userrole__is_active=True
        )

    return qs.distinct()