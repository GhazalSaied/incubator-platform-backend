from rest_framework.exceptions import ValidationError

from ideas.models import Idea, ExhibitionSubmission, IdeaStatus, Season


class ExhibitionPublicService:

    @staticmethod
    def get_latest_season():
        return Season.objects.order_by("-end_date").first()

    @staticmethod
    def get_projects(sector=None):
        season = ExhibitionPublicService.get_latest_season()

        qs = ExhibitionSubmission.objects.select_related("project").filter(
            project__status=IdeaStatus.GRADUATED_POSITIVE,
            status="approved",
            project__season=season
        )

        if sector:
            qs = qs.filter(project__sector__iexact=sector)

        return qs

    @staticmethod
    def get_project_details(submission_id):
        try:
            submission = ExhibitionSubmission.objects.select_related("project").get(
                id=submission_id,
                status="approved",
                project__status=IdeaStatus.GRADUATED_POSITIVE
            )
        except ExhibitionSubmission.DoesNotExist:
            raise ValidationError("Project not found")

        return submission