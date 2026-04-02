from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ideas.models import Idea
from incubator_admin.serializers.evaluation import IdeaEvaluationListSerializer
from core.permissions import IsAdminOrSecretary
from accounts.models import User
from evaluations.models import IdeaEvaluator,IdeaEvaluatorRequest
from notifications.models import Notification
from django.db import models
#\\\\\\عرض الافكار لتعيين مقيمين \\\\\
class IdeasForEvaluationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        # 🔥 فلترة أساسية: فقط المقبولة من المعسكر
        ideas = Idea.objects.filter(bootcamp_status="accepted")

        # 🔥 فلترة حسب القطاع (اختياري)
        sector = request.query_params.get("sector")

        if sector:
            ideas = ideas.filter(sector=sector)

        serializer = IdeaEvaluationListSerializer(ideas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
 #\\\\\\عرض المتطوعين لاختيار مقيمين\\\\\
class VolunteersListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        skill = request.query_params.get("skill")

        volunteers = User.objects.filter(
            userrole__role__code="VOLUNTEER",
            userrole__is_active=True,
        ).filter(
            models.Q(userrole__expires_at__isnull=True) |
            models.Q(userrole__expires_at__gt=timezone.now())
        ).filter(
            volunteer_profile__status="APPROVED"
        )

        # 🔥 فلترة حسب المهارة
        if skill:
            volunteers = volunteers.filter(
                volunteer_profile__primary_skills__icontains=skill
            )

        volunteers = volunteers.distinct()

        data = [
            {
                "id": v.id,
                "name": v.full_name,
                "primary_skills": getattr(v.volunteer_profile, "primary_skills", None)
            }
            for v in volunteers
        ]

        return Response(data)  
    
    
#\\\\\تعيين مقيمين للفكرة\\\\\
class AssignEvaluatorsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request, idea_id):

        evaluator_ids = request.data.get("evaluators", [])

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response({"error": "Idea not found"}, status=404)

        created_requests = []

        for user_id in evaluator_ids:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                continue

            # 🔥 تحقق أنه متطوع approved
            is_volunteer = User.objects.filter(
                id=user.id,
                userrole__role__code="VOLUNTEER",
                userrole__is_active=True,
            ).filter(
                models.Q(userrole__expires_at__isnull=True) |
                models.Q(userrole__expires_at__gt=timezone.now())
            ).filter(
                volunteer_profile__status="APPROVED"
            ).exists()

            if not is_volunteer:
                continue

            request_obj, created = IdeaEvaluatorRequest.objects.get_or_create(
                idea=idea,
                user=user
            )

            if created:
                created_requests.append(user.id)

                # 🔔 إشعار
                Notification.objects.create(
                    user=user,
                    title="طلب تقييم",
                    message=f"تم ترشيحك لتقييم فكرة: {idea.title}"
                )

        return Response({
            "message": "Requests sent",
            "users": created_requests
        }, status=status.HTTP_200_OK)

