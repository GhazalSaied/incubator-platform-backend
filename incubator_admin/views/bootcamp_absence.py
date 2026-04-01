from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ideas.models import Idea
from bootcamp.models import BootcampAttendance,BootcampAbsenceRequest
from core.permissions import IsAdminOrSecretary
from notifications.models import Notification

#\\\\\\\عرض طلبات الغياب \\\\\\

class AbsenceRequestsListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):
        requests = BootcampAbsenceRequest.objects.select_related("idea", "session", "idea__owner")

        data = []
        for r in requests:
            data.append({
                "request_id": r.id,
                "idea_title": r.idea.title,
                "applicant": r.idea.owner.full_name,
                "session_date": r.session.date,
                "reason": r.reason,
                "status": r.status
            })

        return Response(data)
    
    
    
#\\\قرار طلب الغياب\\\\\\
class AbsenceDecisionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request):
        request_id = request.data.get("request_id")
        decision = request.data.get("decision")

        try:
            absence =BootcampAbsenceRequest.objects.get(id=request_id)
        except BootcampAbsenceRequest.DoesNotExist:
            return Response({"detail": "الطلب غير موجود"}, status=404)

        if absence.status != 'pending':
            return Response({"detail": "تم اتخاذ قرار مسبقاً"}, status=400)

        # ✅ قبول
        if decision == 'approve':
            absence.status = 'approved'

            Notification.objects.create(
                user=absence.idea.owner,
                title="طلب الغياب",
                message="تم قبول طلب الغياب الخاص بك ✅"
            )

        # ⚠️ تحذير
        elif decision == 'warn':
            absence.status = 'warned'

            Notification.objects.create(
                user=absence.idea.owner,
                title="تحذير",
                message="تم رفض طلب الغياب ⚠️ يرجى الالتزام بالحضور"
            )

        else:
            return Response({"detail": "قرار غير صالح"}, status=400)

        absence.save()

        return Response({"detail": "تم اتخاذ القرار"})