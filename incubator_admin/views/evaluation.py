from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ideas.models import Idea
from incubator_admin.serializers.evaluation import IdeaEvaluationListSerializer,ScheduleEvaluationSerializer,CreateTemplateCriterionSerializer,EvaluationTemplatePreviewSerializer
from core.permissions import IsAdminOrSecretary
from accounts.models import User
from evaluations.models import IdeaEvaluator,IdeaEvaluatorRequest,EvaluationSession,EvaluationTemplate,EvaluationTemplateCriterion,EvaluationCriterion
from notifications.models import Notification
from django.db import models
from rest_framework import status
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404


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



#\\\\\\\المقيمين للفكرة\\\
class EvaluatorsForIdeaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, idea_id):

        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response({"error": "Idea not found"}, status=404)

        evaluators = idea.assigned_evaluators.filter(status="accepted")

        data = [
            {
                "id": item.evaluator.id,
                "name": item.evaluator.full_name,
                "skills": getattr(item.evaluator.volunteer_profile, "primary_skills", "")
            }
            for item in evaluators
        ]

        return Response(data)
    
    
#\\\\عرض الافكار لتحديد موعد اللجنة \\\
class IdeasForSchedulingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request):

        queryset = Idea.objects.filter(
            bootcamp_status="accepted"
        ).annotate(
            accepted_evaluators_count=Count(
                "assigned_evaluators",
                filter=Q(assigned_evaluators__status="accepted")
            )
        ).filter(
            accepted_evaluators_count__gt=0
        )

        # 🔍 فلترة حسب القطاع
        sector = request.query_params.get("sector")
        if sector:
            queryset = queryset.filter(sector=sector)

        # 🔍 فلترة اختيارية حسب عدد المقيمين
        min_evaluators = request.query_params.get("min_evaluators")
        if min_evaluators:
            queryset = queryset.filter(
                accepted_evaluators_count__gte=min_evaluators
            )

        queryset = queryset.order_by("-created_at")

        serializer = IdeaEvaluationListSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
    
#\\\\تحديد  موعد اللجنة\\\\
class ScheduleEvaluationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request, idea_id):

        # ✅ جلب الفكرة
        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return Response({"error": "الفكرة غير موجودة"}, status=404)

        # ✅ Serializer مع context
        serializer = ScheduleEvaluationSerializer(
            data=request.data,
            context={"idea": idea}
        )
        serializer.is_valid(raise_exception=True)

        scheduled_at = serializer.validated_data["scheduled_at"]

        # ✅ إنشاء الجلسة
        session = EvaluationSession.objects.create(
            idea=idea,
            scheduled_at=scheduled_at,
            created_by=request.user
        )

        # 🟢 جلب المقيمين المقبولين
        evaluators = idea.assigned_evaluators.filter(status="accepted")

        evaluator_users = [item.evaluator for item in evaluators]

        # 🟢 إشعار صاحب الفكرة
        Notification.objects.create(
            user=idea.owner,
            title="تم تحديد موعد التقييم",
            message=f"تم تحديد موعد تقييم فكرتك ({idea.title}) بتاريخ {scheduled_at}"
        )

        # 🟢 إشعارات المقيمين
        notifications = [
            Notification(
                user=user,
                title="موعد تقييم جديد",
                message=f"لديك جلسة تقييم لفكرة ({idea.title}) بتاريخ {scheduled_at}"
            )
            for user in evaluator_users
        ]

        Notification.objects.bulk_create(notifications)

        return Response({
            "message": "تم تحديد الموعد بنجاح",
            "session_id": session.id,
            "scheduled_at": scheduled_at
        }, status=status.HTTP_201_CREATED)
        
        
        
#\\\\اضافة معيار لنموذج التقييم \\\\

class CreateCriterionAndAttachToTemplateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request, template_id):

        template = get_object_or_404(EvaluationTemplate, id=template_id)

        # 🔒 LOCK
        if template.is_published:
            return Response(
                {"error": "لا يمكن التعديل بعد نشر النموذج"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateTemplateCriterionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 🟢 إنشاء معيار جديد
        criterion = EvaluationCriterion.objects.create(
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            max_score=serializer.validated_data.get("max_score", 5),
        )

        # 🟢 ربطه بالنموذج
        EvaluationTemplateCriterion.objects.create(
            template=template,
            criterion=criterion,
            order=serializer.validated_data.get("order", 0)
        )

        return Response({
            "message": "تم إنشاء المعيار وربطه بالنموذج"
        }, status=status.HTTP_201_CREATED)
        
        
        
#\\\\حذف معيار من نموذج التقييم\\\
class RemoveCriterionFromTemplateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def delete(self, request, template_id, criterion_id):

        template = get_object_or_404(EvaluationTemplate, id=template_id)

        # 🔒 LOCK
        if template.is_published:
            return Response(
                {"error": "لا يمكن التعديل بعد نشر النموذج"},
                status=400
            )

        obj = EvaluationTemplateCriterion.objects.filter(
            template=template,
            criterion_id=criterion_id
        ).first()

        if not obj:
            return Response(
                {"error": "المعيار غير موجود في هذا النموذج"},
                status=404
            )

        obj.delete()

        return Response({
            "message": "تم حذف المعيار من النموذج فقط"
        })
        
        
        
#\\\\\معاينة النموذج \\\\
class EvaluationTemplatePreviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get(self, request, template_id):

        template = get_object_or_404(EvaluationTemplate, id=template_id)

        criteria = template.criteria.all()  # مرتب تلقائي بسبب ordering

        serializer = EvaluationTemplatePreviewSerializer(criteria, many=True)

        return Response({
            "template_id": template.id,
            "title": template.title,
            "is_published": template.is_published,
            "criteria": serializer.data
        })
        
#\\\\نشر نموذج التقييم\\\
class PublishEvaluationTemplateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def post(self, request, template_id):

        template = get_object_or_404(EvaluationTemplate, id=template_id)

        # ❌ إذا منشور مسبقاً
        if template.is_published:
            return Response(
                {"error": "النموذج منشور مسبقاً"},
                status=400
            )

        # ❌ لازم يكون فيه معايير
        if template.criteria.count() == 0:
            return Response(
                {"error": "لا يمكن نشر نموذج بدون معايير"},
                status=400
            )

        # 🔥 مهم جداً: إلغاء نشر أي نموذج سابق
        EvaluationTemplate.objects.filter(is_published=True).update(is_published=False)

        # ✅ نشر الحالي
        template.is_published = True
        template.save()

        return Response({
            "message": "تم نشر النموذج بنجاح"
        })