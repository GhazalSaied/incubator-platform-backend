

from evaluations.models import Evaluation, EvaluationAssignment, IncubationAssignment, IncubationReview
from admin_panel.bootcamp.attendance.services import calculate_absence
from admin_panel.incubations.services import IncubationNotesService
from ideas.models import Idea, Season
from volunteers.models import Workshop,VolunteerProfile, WorkshopRegistration
from accounts.models import User,UserRole
from django.db.models import Q


class UsersQueryService:

    @staticmethod
    def get_users(role_code=None):

        admin_ids = UserRole.objects.filter(
            role__code="ADMIN",
            is_active=True
        ).values_list("user_id", flat=True)

        qs = User.objects.exclude(
            id__in=admin_ids
        ).prefetch_related(
            "userrole_set__role"
        ).order_by("-created_at")

        if role_code:
            qs = qs.filter(
                userrole__role__code=role_code,
                userrole__is_active=True
            )

        return qs.distinct()
    @staticmethod
    def get_current_ideas():

        season = Season.objects.filter(
            is_open=True
        ).first()

        if not season:
            return []

        ideas = Idea.objects.filter(
            season=season
        ).only("id", "title")

        return [
            {
                "id": idea.id,
                "title": idea.title
            }
            for idea in ideas
        ]

class UserProfileService:

    WORKSHOP_STATUS_MAP = {
        "rejected": "مرفوض",
        "pending": "قيد المراجعة",
        "accepted": "مقبول",
    }

    # =====================================================
    # MAIN PROFILE
    # =====================================================

    @staticmethod
    def get_user_profile(user):

        return {
            "basic_info": UserProfileService._get_basic_info(user),
            "roles": list(user.role_codes),
            "sections": UserProfileService._build_sections(user)
        }

    # =====================================================
    # SECTIONS BUILDER
    # =====================================================

    @staticmethod
    def _build_sections(user):

        sections = []

        role_codes = set(user.role_codes)

        if "VOLUNTEER" in role_codes:
            sections.append({
                "type": "VOLUNTEER",
                "data": UserProfileService._get_volunteer_data(user)
            })

        if "EVALUATOR" in role_codes:
            sections.append({
                "type": "EVALUATOR",
                "data": UserProfileService._get_evaluator_data(user)
            })

        if "IDEA_OWNER" in role_codes:
            sections.append({
                "type": "IDEA_OWNER",
                "data": UserProfileService._get_idea_owner_data(user)
            })

        if "INCUBATOR" in role_codes:
            sections.append({
                "type": "INCUBATOR",
                "data": UserProfileService._get_incubated_data(user)
            })

        return sections

    # =====================================================
    # BASIC INFO
    # =====================================================

    @staticmethod
    def _get_basic_info(user):

        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar.url if user.avatar else None,
            "joined_at": user.created_at.strftime("%d/%m/%Y"),
            "is_active": user.is_active,
            "current_roles": list(
                user.userrole_set.filter(is_active=True)
                .values_list("role__code", flat=True)
            ),
            "all_roles": list(
                user.userrole_set.values_list(
                    "role__code",
                    flat=True
                ).distinct()
            ),
            
        }

    # =====================================================
    # EVALUATIONS
    # =====================================================

    @staticmethod
    def get_all_evaluations_for_idea(idea):

        evaluations = Evaluation.objects.filter(
            idea=idea,
            is_submitted=True
        ).select_related("evaluator").prefetch_related("scores")

        return [
            {
                "evaluator_name": ev.evaluator.full_name,
                "score": sum(s.score or 0 for s in ev.scores.all()),
                "note": ev.notes,
            }
            for ev in evaluations
        ]

    # =====================================================
    # IDEA OWNER
    # =====================================================

    @staticmethod
    def _get_idea_owner_data(user):

        ideas = user.ideas.all()

        if not ideas.exists():
            return {"ideas": []}

        return {
            "ideas": [
                {
                    "idea_id": idea.id,
                    "title": idea.title,
                    "status": idea.status,
                    "evaluations": UserProfileService.get_all_evaluations_for_idea(idea),
                    "commitment_percentage": round(
                        100 - calculate_absence(idea)[2],
                        2
                    )
                }
                for idea in ideas
            ]
        }

    # =====================================================
    # VOLUNTEER
    # =====================================================

    @staticmethod
    def _get_volunteer_data(user):

        workshops = Workshop.objects.filter(
            created_by=user
        ).order_by("-created_at")

        return {
            "workshops": [
                {
                    "id": w.id,
                    "title": w.title,
                    "start_date": (
                        w.start_date.strftime("%d/%m/%Y")
                        if w.start_date else None
                    ),
                    "status": UserProfileService.WORKSHOP_STATUS_MAP.get(
                        w.status.lower(),
                        w.status
                    )
                }
                for w in workshops
            ]
        }

    # =====================================================
    # EVALUATOR (NO DUPLICATION VERSION)
    # =====================================================

    @staticmethod
    def _get_evaluator_data(user):

        eval_assignments = EvaluationAssignment.objects.filter(
            evaluator=user
        ).select_related("idea")

        inc_assignments = IncubationAssignment.objects.filter(
            mentor=user.volunteer_profile   
        ).select_related("idea")

        # ===============================
        # MERGE IDEAS (NO DUPLICATION)
        # ===============================

        ideas_map = {}

        # Evaluation assignments
        for a in eval_assignments:

            ideas_map.setdefault(a.idea.id, {
                "idea_id": a.idea.id,
                "title": a.idea.title,
                "sector": a.idea.sector,
                "target_audience": a.idea.target_audience,
                "roles": []
            })

            ideas_map[a.idea.id]["roles"].append("EVALUATION")

        # Incubation assignments
        for a in inc_assignments:

            ideas_map.setdefault(a.idea.id, {
                "idea_id": a.idea.id,
                "title": a.idea.title,
                "sector": a.idea.sector,
                "target_audience": a.idea.target_audience,
                "roles": []
            })

            ideas_map[a.idea.id]["roles"].append("INCUBATION")

        return {
            "assignments": list(ideas_map.values())
        }

    # =====================================================
    # INCUBATED
    # =====================================================

    @staticmethod
    def _get_incubated_data(user):

        ideas = Idea.objects.filter(
            owner=user,
            status__in=[
                "GRADUATED_POSITIVE",
                "GRADUATED_NEGATIVE",
                "INCUBATION"
            ]
        )

        if not ideas.exists():
            return {"ideas": []}

        return {
            "ideas": [
                {
                    "idea_id": idea.id,
                    "title": idea.title,
                    "evaluations": UserProfileService.get_all_evaluations_for_idea(idea),
                    "reviews": [
                        {"note": r.notes}
                        for r in idea.reviews.all()
                    ]
                }
                for idea in ideas
            ]
        }