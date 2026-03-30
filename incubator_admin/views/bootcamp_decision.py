from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.permissions import IsAdminOrSecretary
from ideas.models import Idea


class BootcampDecisionView(APIView):
    permission_classes = [IsAuthenticated,IsAdminOrSecretary]

    def post(self, request):
        idea_id = request.data.get("idea_id")
        decision = request.data.get("decision")
        message = request.data.get("message")

        idea = Idea.objects.get(id=idea_id)
        idea.bootcamp_status = decision
        idea.decision_note = message

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response({"detail": "الفكرة غير موجودة"}, status=404)

        # ❗ نتأكد إنو لسا بالمعسكر
        if idea.bootcamp_status != 'pending':
            return Response(
                {"detail": "تم اتخاذ قرار مسبقاً"},
                status=400
            )

        # ✅ قبول → تروح عالتقييم
        if decision == 'accepted':
            idea.bootcamp_status = 'accepted'
            idea.status = 'evaluation'

        elif decision == 'rejected':
            idea.bootcamp_status = 'rejected'
            idea.status = 'rejected'

        else:
            return Response({"detail": "قرار غير صالح"}, status=400)

        idea.save()

        return Response({
            "idea_id": idea.id,
            "bootcamp_status": idea.bootcamp_status,
            "status": idea.status
        })