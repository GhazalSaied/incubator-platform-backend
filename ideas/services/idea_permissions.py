
from rest_framework.permissions import BasePermission
from ideas.models import Idea, IdeaStatus


class CanSubmitIdea(BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        # منع وجود فكرة فعالة
        existing = Idea.objects.filter(
            owner=user
        ).exclude(
            status__in=[
                IdeaStatus.BOOTCAMP_FAILED,
                IdeaStatus.REJECTED
            ]
        ).exists()

        return not existing