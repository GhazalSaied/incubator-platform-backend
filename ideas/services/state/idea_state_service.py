from ideas.models import Idea, IdeaAuditLog
from ideas.services.idea_workflow import IdeaWorkflow
from ideas.services.audit_service import AuditService
from ideas.services.season_phase_service import SeasonPhaseService
from core.events import EventBus
from ideas.models import IdeaStatus
from ideas.phases import SeasonPhase



class IdeaStateService:

    #////////////// بتمنع ال تايميتغ الغلط //////////////////

    PHASE_STATUS_RULES = {
        SeasonPhase.SUBMISSION: [
            IdeaStatus.DRAFT,
            IdeaStatus.SUBMITTED,
            IdeaStatus.WITHDRAWN,
        ],

        SeasonPhase.BOOTCAMP: [
            IdeaStatus.PRE_ACCEPTED,
            IdeaStatus.BOOTCAMP,
            IdeaStatus.BOOTCAMP_FAILED,
        ],

        SeasonPhase.EVALUATION: [
            IdeaStatus.EVALUATION,
            IdeaStatus.EVALUATED,
            IdeaStatus.ACCEPTED,
            IdeaStatus.REJECTED,
        ],

        SeasonPhase.INCUBATION: [
            IdeaStatus.INCUBATION,
        ],

        SeasonPhase.EXHIBITION: [
            IdeaStatus.EXHIBITION,
            IdeaStatus.GRADUATED_POSITIVE,
            IdeaStatus.GRADUATED_NEGATIVE,
        ],
    }


    # الtransition المسموح حسب المرحلة timing
    @staticmethod
    def validate_phase(idea, to_status):

        current_phase = SeasonPhaseService.get_current_phase()

        if not current_phase:
            raise Exception("No active phase")

        allowed_statuses = IdeaStateService.PHASE_STATUS_RULES.get(current_phase.phase, [])

        if to_status not in allowed_statuses:
            raise Exception(
                f"Status {to_status} not allowed in phase {current_phase}"
            )


    #هل الشروط محققة او لا للانتقال business truth
    @staticmethod
    def validate_guards(idea, to_status):

        #  1. لا يمكن قبول فكرة بدون تقييم
        if to_status == IdeaStatus.ACCEPTED:
            if idea.status != IdeaStatus.EVALUATED:
                raise Exception("Idea must be evaluated before acceptance")

        #  2. لا يمكن دخول الاحتضان بدون فريق
        if to_status == IdeaStatus.INCUBATION:
            if not hasattr(idea, "team_members") or idea.team_members.count() == 0:
                raise Exception("Idea must have a team before incubation")

        #  3. لا يمكن عرض فكرة بدون بيانات معرض
        if to_status == IdeaStatus.EXHIBITION:
            if not idea.exhibition_date:
                raise Exception("Exhibition date is required")

        #  4. التخرج الإيجابي يحتاج يكون من exhibition فقط
        if to_status == IdeaStatus.GRADUATED_POSITIVE:
            if idea.status != IdeaStatus.EXHIBITION:
                raise Exception("Invalid graduation flow")
        
        # 5. لا يمكن الانتقال من المرحلة الى المرحلة نفسها
        if idea.status == to_status:
            raise Exception("Already in this status")

            
        # 6. منع السحب في مراحل متقدمة
        if to_status == IdeaStatus.WITHDRAWN:
            if idea.status not in [IdeaStatus.DRAFT, IdeaStatus.SUBMITTED]:
                raise Exception("Cannot withdraw at this stage")
        
        # 7. منع rejection بعد acceptance
        if idea.status == IdeaStatus.ACCEPTED and to_status == IdeaStatus.REJECTED:
            raise Exception("Cannot reject after acceptance")
        
        # 8. منع bootcamp بدون pre_accepted
        if to_status == IdeaStatus.BOOTCAMP:
             if idea.status != IdeaStatus.PRE_ACCEPTED:
                raise Exception("Must be pre-accepted before bootcamp")
             
        # 9. منع evaluation بدون bootcamp
        if to_status == IdeaStatus.EVALUATION:
            if idea.status != IdeaStatus.BOOTCAMP:
                raise Exception("Must pass bootcamp first")
        
        # 10. منع evaluated بدون evaluation
        if to_status == IdeaStatus.EVALUATED:
            if idea.status != IdeaStatus.EVALUATION:
                raise Exception("Must be in evaluation first")
        
        # 11. منع incubation بدون accepted
        if to_status == IdeaStatus.INCUBATION:
            if idea.status != IdeaStatus.ACCEPTED:
                raise Exception("Idea must be accepted first")
        
        # 12. منع exhibition بدون incubation
        if to_status == IdeaStatus.EXHIBITION:
            if idea.status != IdeaStatus.INCUBATION:
                raise Exception("Must be in incubation first")
            
    




    @staticmethod
    def change_status(*, idea: Idea, to_status: str, user=None, source="system", reason=None, metadata=None):

        old_status = idea.status

        # 1. validate transition
        IdeaWorkflow.validate_transition(old_status, to_status)
        
        # 2. phase validation
        IdeaStateService.validate_phase(idea, to_status)
           
        # 3. guards 
        IdeaStateService.validate_guards(idea, to_status)
        

        # 4. apply state
        idea.status = to_status
        idea.save(update_fields=["status"])

        # 5. audit (single source)
        IdeaAuditLog.objects.create(
            idea=idea,
            from_status=old_status,
            to_status=to_status,
            performed_by=user,
            reason=reason
        )

        # 6. event
        EventBus.emit(
            "idea_status_changed",
            payload={
                "idea": idea,
                "new_status": to_status,
            },
            actor=user,
        )

        return idea
    
