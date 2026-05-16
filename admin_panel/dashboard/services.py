# statistics/services/overview_service.py

from datetime import datetime, date

from django.db.models import Count

from accounts.models import User

from ideas.models import (
    Idea,
    IdeaAuditLog,
    IdeaStatus,
    Season
)

from ideas.services.season_phase_service import (
    SeasonPhaseService
)

from volunteers.models import (
    VolunteerAvailability,
    VolunteerProfile
)


# =========================================================
# KPI REPOSITORY
# =========================================================

class KPIRepository:

    # =====================================================
    # IDEAS
    # =====================================================

    @staticmethod
    def total_ideas(season):

        return (
            Idea.objects
            .filter(season=season)
            .count()
        )

    # =====================================================

    @staticmethod
    def submitted_ideas(season):

        return (
            Idea.objects
            .filter(season=season)
            .exclude(status=IdeaStatus.DRAFT)
            .count()
        )

    # =====================================================
    # STATUS TRANSITIONS
    # =====================================================

    @staticmethod
    def count_status_transition(
        season,
        to_status,
        distinct=True
    ):

        qs = (
            IdeaAuditLog.objects
            .filter(
                idea__season=season,
                to_status=to_status
            )
        )

        if distinct:
            qs = qs.values("idea").distinct()

        return qs.count()

    # =====================================================

    @staticmethod
    def incubated_projects(season):

        return KPIRepository.count_status_transition(
            season,
            IdeaStatus.INCUBATION
        )

    # =====================================================

    @staticmethod
    def graduated_projects(season):

        return KPIRepository.count_status_transition(
            season,
            IdeaStatus.GRADUATED_POSITIVE
        )

    # =====================================================

    @staticmethod
    def bootcamp_projects(season):

        return KPIRepository.count_status_transition(
            season,
            IdeaStatus.BOOTCAMP
        )

    # =====================================================
    # SECTORS
    # =====================================================

    @staticmethod
    def sector_distribution(season):

        return (
            Idea.objects
            .filter(season=season)
            .exclude(sector__isnull=True)
            .exclude(sector="")
            .values("sector")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

    # =====================================================
    # VOLUNTEERS
    # =====================================================

    @staticmethod
    def volunteers_count():

        return (
            User.objects
            .filter(
                userrole__role__code="VOLUNTEER",
                userrole__is_active=True
            )
            .distinct()
            .count()
        )

    # =====================================================
    # SEASONS
    # =====================================================

    @staticmethod
    def seasons():

        return (
            Season.objects
            .exclude(status="DRAFT")
            .order_by("start_date")
        )


# =========================================================
# OVERVIEW STATISTICS
# =========================================================

class OverviewStatisticsService:

    @staticmethod
    def get():

        seasons = KPIRepository.seasons()

        return [
            {
                "season_id": season.id,
                "year": season.start_date.year,
                "season_name": season.name,

                "total_projects": (
                    KPIRepository.total_ideas(season)
                ),

                "incubated_projects": (
                    KPIRepository.incubated_projects(season)
                ),

                "graduated_projects": (
                    KPIRepository.graduated_projects(season)
                ),

                "volunteer_hours": (
                    OverviewStatisticsService
                    ._calculate_volunteer_hours()
                )
            }
            for season in seasons
        ]

    # =====================================================

    @staticmethod
    def _calculate_volunteer_hours():

        total_hours = 0

        availabilities = (
            VolunteerAvailability.objects.all()
        )

        for availability in availabilities:

            start = datetime.combine(
                date.today(),
                availability.start_time
            )

            end = datetime.combine(
                date.today(),
                availability.end_time
            )

            duration = end - start

            total_hours += (
                duration.total_seconds() / 3600
            )

        return round(total_hours, 2)


# =========================================================
# LIFECYCLE STATISTICS
# =========================================================

class LifecycleStatisticsService:

    @staticmethod
    def get():

        seasons = KPIRepository.seasons()

        return [
            {
                "season_id": s.id,
                "year": s.start_date.year,
                "season_name": s.name,

                "submitted": (
                    KPIRepository.submitted_ideas(s)
                ),

                "bootcamp": (
                    KPIRepository.bootcamp_projects(s)
                ),

                "incubated": (
                    KPIRepository.incubated_projects(s)
                ),

                "graduated": (
                    KPIRepository.graduated_projects(s)
                ),
            }
            for s in seasons
        ]


# =========================================================
# SECTOR STATISTICS
# =========================================================

class SectorStatisticsService:

    @staticmethod
    def get():

        seasons = KPIRepository.seasons()

        result = []

        for s in seasons:

            sectors = (
                KPIRepository
                .sector_distribution(s)
            )

            total = sum(
                item["count"]
                for item in sectors
            )

            sector_result = []

            for item in sectors:

                percentage = 0

                if total > 0:

                    percentage = round(
                        (item["count"] / total) * 100,
                        1
                    )

                sector_result.append({
                    "sector": item["sector"],
                    "count": item["count"],
                    "percentage": percentage
                })

            result.append({
                "season_id": s.id,
                "year": s.start_date.year,
                "season_name": s.name,
                "total_projects": total,
                "sectors": sector_result
            })

        return result


# =========================================================
# EXPERTISE STATISTICS
# =========================================================

class ExpertiseStatisticsService:

    @staticmethod
    def get():

        rows = (
            VolunteerProfile.objects
            .filter(
                status=VolunteerProfile.APPROVED
            )
            .values("primary_skills")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        total = sum(
            item["count"]
            for item in rows
        )

        result = []

        choices_map = dict(
            VolunteerProfile._meta
            .get_field("primary_skills")
            .choices
        )

        for item in rows:

            skill_code = item["primary_skills"]

            percentage = 0

            if total > 0:

                percentage = round(
                    (item["count"] / total) * 100,
                    1
                )

            result.append({
                "skill": skill_code,

                "label": choices_map.get(skill_code),

                "count": item["count"],

                "percentage": percentage
            })

        return {
            "total_volunteers": total,
            "skills": result
        }


# =========================================================
# SEASON COMPARISON
# =========================================================

class SeasonComparisonService:

    @staticmethod
    def get():

        result = []

        for season in KPIRepository.seasons():

            result.append({
                "year": season.start_date.year,

                "season_id": season.id,

                "season_name": season.name,

                "incubated_projects": (
                    KPIRepository
                    .incubated_projects(season)
                ),

                "graduated_projects": (
                    KPIRepository
                    .graduated_projects(season)
                )
            })

        return result


# =========================================================
# CURRENT SEASON STATISTICS
# =========================================================

class CurrentSeasonStatisticsService:

    @staticmethod
    def get():

        current_season = (
            SeasonPhaseService
            .get_current_season()
        )

        if not current_season:

            return {
                "submitted_projects": 0,
                "incubated_projects": 0,
                "graduated_projects": 0,
                "volunteers_count": 0
            }

        return {
            "season_id": current_season.id,

            "season_name": current_season.name,

            "submitted_projects": (
                KPIRepository
                .submitted_ideas(current_season)
            ),

            "incubated_projects": (
                KPIRepository
                .incubated_projects(current_season)
            ),

            "graduated_projects": (
                KPIRepository
                .graduated_projects(current_season)
            ),

            "volunteers_count": (
                KPIRepository
                .volunteers_count()
            )
        }


# =========================================================
# GRADUATED PROJECTS CHART
# =========================================================

class GraduatedProjectsChartService:

    @staticmethod
    def get():

        result = []

        for season in KPIRepository.seasons():

            result.append({
                "season_id": season.id,

                "year": season.start_date.year,

                "season_name": season.name,

                "graduated_projects": (
                    KPIRepository
                    .graduated_projects(season)
                )
            })

        return result


from django.contrib.auth import get_user_model

from core.events import EventBus

User = get_user_model()


class AdminBroadcastService:

    ROLE_MAP = {
        "VOLUNTEERS": "VOLUNTEER",
        "EVALUATORS": "EVALUATOR",
        "INCUBATORS": "INCUBATOR",
        "IDEA_OWNERS": "IDEA_OWNER",
    }

    # =====================================================

    @staticmethod
    def send(*, target, message):

        users = (
            AdminBroadcastService
            ._get_target_users(target)
        )

        EventBus.emit(
            "ADMIN_BROADCAST_NOTIFICATION",

            users=users,

            message=message
        )

        return users.count()

    # =====================================================

    @staticmethod
    def _get_target_users(target):

        # =====================================
        # ALL USERS
        # =====================================

        if target == "ALL":

            return (
                User.objects
                .filter(is_active=True)
                .exclude(
                    userrole__role__code="ADMIN"
                )
                .distinct()
            )

        # =====================================
        # ROLE USERS
        # =====================================

        role_code = (
            AdminBroadcastService
            .ROLE_MAP
            .get(target)
        )

        if not role_code:
            return User.objects.none()

        return (
            User.objects
            .filter(
                is_active=True,

                userrole__role__code=role_code,

                userrole__is_active=True
            )
            .distinct()
        )