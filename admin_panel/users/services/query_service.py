

from evaluations.models import Evaluation
from admin_panel.bootcamp.attendance.services import calculate_absence
from admin_panel.incubations.services import IncubationNotesService
from volunteers.models import Workshop,VolunteerProfile, WorkshopRegistration
from accounts.models import User
from django.db.models import Q




class UsersQueryService:

    @staticmethod
    def get_users(role_code=None):

        qs = User.objects.all().order_by("-created_at")

        # 🚫 استبعاد المديرين (DIRECTOR)
        qs = qs.exclude(
            userrole__role__code="DIRECTOR",
            userrole__is_active=True
        )

        # 🎯 فلترة حسب role إذا مطلوب
        if role_code:
            qs = qs.filter(
                userrole__role__code=role_code,
                userrole__is_active=True
            )

        return qs.distinct()
    
class UserProfileService:

    @staticmethod
    def get_user_profile(user):

        data = {
            "basic_info": UserProfileService._get_basic_info(user),
            "roles": list(user.role_codes)
        }
        request = VolunteerProfile.objects.filter(user=user).first()

        data["VolunteerProfile"] = {
            "id": request.id if request else None
        }

        # 🔥 توزيع حسب الأدوار
        if "IDEA_OWNER" in user.role_codes:
            data["idea_owner_data"] = UserProfileService._get_idea_owner_data(user)

        if user.userrole_set.filter(is_active=True,role__is_volunteer_role=True).exists():
    
            data["volunteer_data"] = UserProfileService._get_volunteer_data(user)
        if "INCUBATED" in user.role_codes:
            data["incubated_data"] = UserProfileService._get_incubated_data(user)

        return data
    @staticmethod
    def _get_basic_info(user):

        return {
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "roles": list(user.role_codes)
        }
        
        

    @staticmethod
    def get_all_evaluations_for_idea(idea):

        evaluations = Evaluation.objects.filter(
            idea=idea,
            is_submitted=True
        ).select_related("evaluator").prefetch_related("scores").order_by("submitted_at")

        result = []

        for ev in evaluations:
            total_score = sum(
                s.score for s in ev.scores.all() if s.score
            )

            result.append({
                "evaluator_name": ev.evaluator.full_name,
                "score": total_score,
                "note": ev.notes,
                "date": ev.submitted_at
            })

        return result
    @staticmethod
    def _get_idea_owner_data(user):
    

    # ✅ القديم (ما لمسناه)
        idea = user.ideas.first()
        if not idea:
            return {}
        total, absent, percentage = calculate_absence(idea)
        commitment = 100 - percentage

    # 🔥 الجديد
        evaluations = UserProfileService.get_all_evaluations_for_idea(idea)

        return {
            "idea_id": idea.id if idea else None,
            "idea_title": idea.title if idea else None,
            "idea.status": idea.status if idea else None,
            "commitment_percentage": round(commitment, 2),

        # 🔥 الجديد
            "evaluations": evaluations
        }
    

    
    @staticmethod  
    def get_last_review_notes_only(idea):

        data = IncubationNotesService.get_latest_review_notes(idea=idea)

        if not data or not data.get("review"):
            return None

        return data["review"].get("notes")
        
    @staticmethod
    def _get_incubated_data(user):

        idea = user.ideas.filter(status="INCUBATION").first()

        if not idea:
            return {}

        last_review = UserProfileService.get_last_review_notes_only(idea)

        evaluations = UserProfileService.get_all_evaluations_for_idea(idea)

        return {
            "idea_id": idea.id if idea else None,
            "idea_title": idea.title if idea else None,
            "idea.status": idea.status if idea else None,
            "last_review_note": last_review,
            "evaluations": evaluations
        }
        
    @staticmethod  
    def get_user_workshops(user):
        return Workshop.objects.filter(created_by=user).values(
            'id',
            'title',
            'category',
            'start_date',
            'end_date',
            'status',
    )
        
    @staticmethod
    def _get_volunteer_data(user):

        workshops = UserProfileService.get_user_workshops(user)

        return [
            {
                "workshops": workshops if workshops else []
            }
            
    ]
        


from django.shortcuts import get_object_or_404


class WorkshopService:

    @staticmethod
    def get_workshop_details_for_volunteer(workshop_id):
        
        workshop = get_object_or_404(
            Workshop,
            id=workshop_id,
            
        )

        data = {
            "title": workshop.title,
            "description": workshop.description,
            "objectives": workshop.objectives,
            "status": workshop.status,
            "start_date": workshop.start_date,
            "end_date": workshop.end_date,
            "target_audience": workshop.target_audience,
            "time_from": workshop.time_from,
            "time_to": workshop.time_to,
            "duration": workshop.duration,
            "capacity": workshop.capacity,
            "category": workshop.category,
            "created_by": workshop.created_by.full_name
            
        }

        if workshop.status == "PENDING":
            data["can_decide"] = True

        elif workshop.status == "ACCEPTED":
            registrations = WorkshopRegistration.objects.filter(workshop=workshop)

            data["attendees"] = [
                {
                    "name": r.name,
                    "email": r.email
                }
                for r in registrations
            ]

        return data