from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone

from ideas.models import Idea, IdeaStatus, Season
from accounts.models import Role, UserRole   # غيري المسار إذا كان Role في مكان آخر

User = get_user_model()


class AdminDashboardStats(APIView):
    """
    إرجاع إحصائيات لوحة التحكم الرئيسية
    حاليًا: عدد المستخدمين + عدد المتقدمين في الموسم الحالي (SUBMITTED فقط)
    """

    permission_classes = []
    
    
    def get(self, request):
        # ----------------------------------------------------------------
        # 1. إحصائيات المستخدمين
        # ----------------------------------------------------------------
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()

        # عدد المتطوعين (كل roles اللي is_volunteer_role=True)
        volunteer_roles = Role.objects.filter(is_volunteer_role=True)
        volunteers_count = UserRole.objects.filter(
            role__in=volunteer_roles,
            is_active=True
        ).values('user_id').distinct().count()

        # ----------------------------------------------------------------
        # 2. عدد المتقدمين في الموسم الحالي (SUBMITTED فقط)
        # ----------------------------------------------------------------
        today = timezone.now().date()

        # البحث عن الموسم اللي يشمل اليوم الحالي
        current_season = Season.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).order_by('-start_date').first()

        # لو ما وجد → نأخذ أحدث موسم
        if not current_season:
            current_season = Season.objects.order_by('-start_date').first()

        if current_season:
            submitted_applicants = Idea.objects.filter(
                season=current_season,
                status=IdeaStatus.SUBMITTED
            ).count()

            current_season_name = current_season.name
            current_season_is_open = current_season.is_open
        else:
            submitted_applicants = 0
            current_season_name = "لا يوجد موسم حالي"
            current_season_is_open = False

        # ----------------------------------------------------------------
        # البيانات اللي رح ترجع
        # ----------------------------------------------------------------
        data = {
            "total_registered_users": total_users,
            "active_users": active_users,
            "volunteers_count": volunteers_count,

            "submitted_applicants_current_season": submitted_applicants,
            "current_season_name": current_season_name,
            "current_season_is_open": current_season_is_open,

            # إحصائيات المشاريع مؤقتة (ما في موديل Project بعد)
            "incubated_projects": 0,
            "graduated_projects": 0,
            "total_projects": 0,

            # جراف سنوي مؤقت
            "yearly_projects": [
                {"year": str(timezone.now().year - i), "count": 0}
                for i in range(6)
            ],
        }

        return Response(data, status=status.HTTP_200_OK)