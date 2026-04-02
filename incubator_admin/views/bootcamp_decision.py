from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.permissions import IsAdminOrSecretary
from ideas.models import Idea,IdeaStatus
from bootcamp.models import BootcampDecision,BootcampAttendance
from notifications.models import Notification
from ideas.phases import SeasonPhase
from ideas.services.season_phase_service import SeasonPhaseService

#\\\\\\\\قائمة المشاركين بالمعسكر\\\\\\\\\\

class BootcampIdeasListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):
        if not SeasonPhaseService.is_phase(SeasonPhase.BOOTCAMP):
            return Response({"detail": "هذه الصفحة متاحة فقط خلال مرحلة المعسكر"},status=403)
        search = request.query_params.get("search", "")

        # فقط الأفكار داخل المعسكر
        ideas = Idea.objects.filter(bootcamp_status__in=['pending', 'accepted'])

        # 🔍 فلترة بالاسم
        if search:
            ideas = ideas.filter(title__icontains=search)

        result = []

        for idea in ideas:
            total = BootcampAttendance.objects.filter(idea=idea).count()
            absent = BootcampAttendance.objects.filter(
                idea=idea,
                status='absent'
            ).count()

            absence = (absent / total * 100) if total > 0 else 0
            commitment = 100 - absence

            result.append({
                "idea_id": idea.id,
                "idea_title": idea.title,

                # 🔥 المطلوب بالواجهة
                "absence_percentage": round(absence, 2),
                "commitment_status": "ملتزم" if commitment >= 70 else "غير ملتزم",

                # 👇 لزر القرار
                "bootcamp_status": idea.bootcamp_status
            })

        return Response(result)
    
    
    
    #\\\\اتخاذ القرار\\\\\

class BootcampDecisionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request):
        idea_id = request.data.get("idea_id")
        decision = request.data.get("decision")
        message = request.data.get("message")

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response({"detail": "الفكرة غير موجودة"}, status=404)

        # 🔥 تحقق من المرحلة
        if not SeasonPhaseService.is_phase(SeasonPhase.BOOTCAMP):
            return Response({"detail": "ليس وقت اتخاذ القرار"}, status=400)

        # 🔥 تحقق من الحالة الأساسية
        if idea.status != IdeaStatus.UNDER_REVIEW:
            return Response({"detail": "الفكرة ليست ضمن المعسكر"}, status=400)

        # 🔥 تحقق من القرار السابق
        if idea.bootcamp_status != 'pending':
            return Response({"detail": "تم اتخاذ قرار مسبقاً"}, status=400)

        # 🔥 القرار
        if decision == 'approve':
            idea.bootcamp_status = 'accepted'

        elif decision == 'reject':
            idea.bootcamp_status = 'rejected'
            idea.status = IdeaStatus.REJECTED

        else:
            return Response({"detail": "قرار غير صالح"}, status=400)

        idea.decision_note = message
        idea.save()

        # 🔔 إشعار
        Notification.objects.create(
            user=idea.owner,
            title="قرار المعسكر",
            message=message
        )

        return Response({
            "idea_id": idea.id,
            "bootcamp_status": idea.bootcamp_status,
            "status": idea.status
        })