from bootcamp.models import BootcampAttendance
from ideas.models import Idea, IdeaStatus

#\\\\\\\\حساب الغياب\\\\\\\\
def calculate_absence(idea):
    total = BootcampAttendance.objects.filter(idea=idea).count()

    absent = BootcampAttendance.objects.filter(
        idea=idea,
        status="absent"
    ).count()

    percentage = (absent / total * 100) if total > 0 else 0

    return total, absent, percentage

#\\\\\attendance list\\\\\\
def get_session_attendance(session_id):
    return BootcampAttendance.objects.filter(session_id=session_id).select_related("idea")

#\\\\\stats\\\\
def get_idea_stats(idea_id):
    idea = Idea.objects.get(id=idea_id)
    total, absent, percentage = calculate_absence(idea)

    return {
        "total_sessions": total,
        "absent_sessions": absent,
        "absence_percentage": percentage
    }
    
#\\\\\\\\participants\\\\\
def get_bootcamp_participants():
    ideas = Idea.objects.filter(
        status__in=[
            IdeaStatus.PRE_ACCEPTED,
            IdeaStatus.BOOTCAMP_FAILED
        ]
    ).select_related("owner")
    
    result = []
    

    for idea in ideas:
        total, absent, percentage = calculate_absence(idea)
        commitment = 100 - percentage
        if idea.status == IdeaStatus.PRE_ACCEPTED:
            bootcamp_status = "مقبول"
        elif idea.status == IdeaStatus.BOOTCAMP_FAILED:
            bootcamp_status = "مرفوض"
        else:
            bootcamp_status = "غير معروف"
        
            

        result.append({
            "idea_id": idea.id,
            "idea_title": idea.title,
            "owner": idea.owner.full_name,
            "commitment_percentage": round(commitment, 2),
            "bootcamp_status": bootcamp_status
            
        })

    return result