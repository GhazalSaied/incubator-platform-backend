from bootcamp.models import BootcampAttendance

class AttendanceService:

    @staticmethod
    def get_stats(idea):
        total = BootcampAttendance.objects.filter(idea=idea).count()
        absent = BootcampAttendance.objects.filter(
            idea=idea,
            status="absent"
        ).count()

        percentage = (absent / total) * 100 if total else 0

        return {
            "total_sessions": total,
            "absent_sessions": absent,
            "attendance_percentage": round(100 - percentage, 2)
        }