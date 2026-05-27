from core.events import EventBus
from ideas.models import (
    Idea,
    IdeaStatus,
    TeamMember,
    ExhibitionSubmission,
)


class ExhibitionService:
    @staticmethod
    def get_user_exhibition_idea(user):
        owner_idea = (
            Idea.objects
            .filter(
                owner=user,
                status=IdeaStatus.EXHIBITION
            )
            .select_related("season")
            .first()
        )

        if owner_idea:
            return owner_idea, True

        member = (
            TeamMember.objects
            .select_related("idea", "idea__season")
            .filter(
                user=user,
                idea__status=IdeaStatus.EXHIBITION
            )
            .first()
        )

        if member:
            return member.idea, False

        raise ValueError(
            "غير مؤهل للوصول إلى مرحلة المعرض"
        )

    @staticmethod
    def get_exhibition_dashboard(user):
        idea, is_owner = (
            ExhibitionService.get_user_exhibition_idea(user)
        )

        form = getattr(
            idea.season,
            "exhibition_form",
            None
        )

        if not form or not form.is_active:
            raise ValueError(
                "نموذج المعرض غير متاح حالياً"
            )

        submission = (
            ExhibitionSubmission.objects
            .filter(project=idea)
            .first()
        )

        return {
            "idea": idea,
            "form": form,
            "submission": submission,
            "is_owner": is_owner,
        }

    @staticmethod
    def create_submission( *, idea, form, submitted_data, ):
        submission = ExhibitionSubmission.objects.create(
            project=idea,
            form=form,
            data=submitted_data,
            status="pending", )
        # ========================= # NOTIFICATION EVENT # =========================
        EventBus.emit( "exhibition_submission_created", submission=submission, actor=idea.owner )
        return submission