from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import status
from django.utils.timezone import now

from core.permissions import CanSubmitIdea
from .models import Idea, Season , IdeaStatus
from .serializers import (
    IdeaFormSerializer,
    IdeaCreateUpdateSerializer,
    IdeaDetailSerializer,
    MyIdeaListSerializer,
)
from notifications.models import Notification
from ideas.services.idea_validation import IdeaFormValidator
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases  import SeasonPhase
from bootcamp.serializers import BootcampSessionSerializer
from bootcamp.models import BootcampSession
from evaluations.models import IncubationReview
from evaluations.serializers import IncubationReviewSerializer


#///////////////////////////GET CUURENT IDEA FORM /////////////////////////////////

class CurrentIdeaFormAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        season = Season.objects.filter(is_open=True).first()
        if not season or not hasattr(season, 'form'):
            return Response(
                {"detail": "لا يوجد موسم مفتوح حالياً"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = IdeaFormSerializer(season.form)
        return Response(serializer.data)

#/////////////////////////// CREATE IDEA VIEW /////////////////////////////////

class IdeaCreateAPIView(APIView):
    permission_classes = [CanSubmitIdea]

    def post(self, request):
        #  تحقق من وجود موسم مفتوح
        season = Season.objects.filter(is_open=True).first()
        if not season or not hasattr(season, "form"):
            return Response(
                {"detail": "التقديم مغلق حالياً"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Validate basic fields (title, description, answers)

        serializer = IdeaCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data.get("answers", {})

        #  Dynamic Form Validation

        try:
            validator = IdeaFormValidator(season.form, answers)
            validator.validate()
        except ValueError as e:
            return Response(
                {"errors": e.args[0]},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Create Idea

        idea = serializer.save(
            owner=request.user,
            season=season,
            status=IdeaStatus.SUBMITTED
        )

        #  Notification

        Notification.objects.create(
            user=request.user,
            title="تم استلام فكرتك",
            message="تم إرسال فكرتك بنجاح وهي قيد المراجعة",
            related_object_id=idea.id,
            related_object_type="IDEA"
        )

        return Response(
            IdeaDetailSerializer(idea).data,
            status=status.HTTP_201_CREATED
        )


#///////////////////////// EDIT IDEA VIEW ///////////////////////////////////

class IdeaUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, idea_id):

        #  جلب الفكرة والتأكد من الملكية
        try:
            idea = Idea.objects.get(id=idea_id, owner=request.user)
        except Idea.DoesNotExist:
            return Response(
                {"detail": "الفكرة غير موجودة أو لا تملك صلاحية تعديلها"},
                status=status.HTTP_404_NOT_FOUND
            )

        #  التحقق من مرحلة الموسم
        if not SeasonPhaseService.is_phase(SeasonPhase.SUBMISSION):
            return Response(
                {"detail": "لا يمكن تعديل الفكرة خارج مرحلة التقديم"},
                status=status.HTTP_403_FORBIDDEN
            )

        #  التحقق من حالة الفكرة
        if not idea.can_be_edited():
            return Response(
                {"detail": "لا يمكن تعديل الفكرة في حالتها الحالية"},
                status=status.HTTP_403_FORBIDDEN
            )

        #  التعديل
        serializer = IdeaCreateUpdateSerializer(
            idea,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            IdeaDetailSerializer(idea).data,
            status=status.HTTP_200_OK
        )


 #////////////////////////  WITHDRIDEAVIEW //////////////////////////////////////////

class WithdrawIdeaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, idea_id):
        #  جلب الفكرة والتأكد من الملكية
        try:
            idea = Idea.objects.get(id=idea_id, owner=request.user)
        except Idea.DoesNotExist:
            return Response(
                {"detail": "الفكرة غير موجودة أو لا تملك صلاحية الوصول إليها"},
                status=status.HTTP_404_NOT_FOUND
            )

        #  التحقق من مرحلة الموسم
        if not SeasonPhaseService.is_phase(SeasonPhase.SUBMISSION):
            return Response(
                {"detail": "لا يمكن سحب الفكرة خارج مرحلة التقديم"},
                status=status.HTTP_403_FORBIDDEN
            )

        #  التحقق من حالة الفكرة
        if idea.status not in [
            IdeaStatus.DRAFT,
            IdeaStatus.SUBMITTED
        ]:
            return Response(
                {"detail": "لا يمكن سحب هذه الفكرة في حالتها الحالية"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  سحب الفكرة
        idea.status = IdeaStatus.WITHDRAWN
        idea.save()

        return Response(
            {"detail": "تم سحب الفكرة بنجاح"},
            status=status.HTTP_200_OK
        )


#///////////////////////////////// CURRENT SEASON PHASE ////////////////////////////////////////

class CurrentSeasonPhaseAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        season = SeasonPhaseService.get_current_season()
        phase = SeasonPhaseService.get_current_phase(season)

        if not season or not phase:
            return Response({
                "season": None,
                "phase": None
            })

        return Response({
            "season": {
                "id": season.id,
                "name": season.name
            },
            "phase": {
                "code": phase.phase,
                "start_date": phase.start_date,
                "end_date": phase.end_date
            }
        })

#//////////////////////////// MY IDEA VIEW (DISPLAY IDEA INFO TO THE USER ) /////////////////////////////////////

class MyIdeasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ideas = Idea.objects.filter(
            owner=request.user
        ).order_by("-created_at")

        serializer = MyIdeaListSerializer(ideas, many=True)
        return Response(serializer.data)

#////////////////////////////////// IDEA DASHBOARD VIEW  //////////////////////////

class IdeaDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            idea = Idea.objects.get(owner=request.user)
        except Idea.DoesNotExist:
            return Response({"detail": "لا يوجد فكرة"}, status=404)

        phase_obj = SeasonPhaseService.get_current_phase()
        phase = phase_obj.phase if phase_obj else "SUBMISSION"

        progress = ["SUBMISSION", "BOOTCAMP", "EVALUATION", "INCUBATION", "EXHIBITION"]

        #  SUBMISSION
        if phase == "SUBMISSION":
            return Response({
                "phase": phase,
                "progress": progress,
                "data": {
                    "message": "تم إرسال فكرتك، بانتظار بدء المعسكر"
                }
            })

        #  BOOTCAMP
        if phase == "BOOTCAMP":

            sessions = BootcampSession.objects.filter(
                phase__phase="BOOTCAMP"
            ).order_by("start_time")

            next_session = sessions.filter(
                start_time__gte=now()
            ).first()

            return Response({
                "phase": phase,
                "progress": progress,
                "data": {
                    "attendance_required": 75,
                    "next_session": BootcampSessionSerializer(next_session).data if next_session else None,
                    "sessions": BootcampSessionSerializer(sessions, many=True).data,
                    "can_request_absence": True
                }
            })

        #  EVALUATION
        if phase == "EVALUATION":
            return Response({
                "phase": phase,
                "progress": progress,
                "data": {
                    "status": "بانتظار التقييم",
                    "meeting_date": None,
                    "notes": None,
                    "can_request_consultation": True
                }
            })

        #  INCUBATION
        if idea.status == IdeaStatus.INCUBATED:

            reviews = idea.reviews.order_by("-meeting_date")
            next_review = reviews.first()

            return Response({
                "phase": "INCUBATION",
                "progress": progress,
                "data": {
                    "warning": "عدم تحقيق تقدم قد يؤدي لإنهاء الاحتضان",
                    "next_review": IncubationReviewSerializer(next_review).data if next_review else None,
                    "reviews": IncubationReviewSerializer(reviews, many=True).data,
                    "can_request_consultation": True
                }
            })
        
        #EXHIBITION
        if phase == "EXHIBITION":
            return Response({
                "phase": phase,
                "progress": progress,
                "data": {
                    "message": "يرجى تجهيز بطاقة المشروع للمعرض",
                    "can_edit": True
                }
            })

        return Response({
            "phase": phase,
            "progress": progress,
            "data": {}
        })
        

        
    
#//////////////////////////// INCUBATION PHASE //////////////////////////

class IncubationPhaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            idea = Idea.objects.get(owner=request.user)
        except Idea.DoesNotExist:
            return Response({"detail": "لا يوجد فكرة"}, status=404)

        if idea.status != IdeaStatus.INCUBATED:
            return Response({"detail": "لم يتم الاحتضان بعد"})

        reviews = idea.reviews.order_by("-meeting_date")

        next_review = reviews.first()

        return Response({
            "phase": "INCUBATION",
            "warning": "عدم تحقيق تقدم قد يؤدي لإنهاء الاحتضان",
            "next_review": IncubationReviewSerializer(next_review).data if next_review else None,
            "reviews": IncubationReviewSerializer(reviews, many=True).data,
            "can_request_consultation": True
        })

#//////////////////////////////// EXHIBITION PHASE /////////////////////////////

class ExhibitionPhaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            idea = Idea.objects.get(owner=request.user)
        except Idea.DoesNotExist:
            return Response({"detail": "لا يوجد فكرة"}, status=404)

        return Response({
            "phase": "EXHIBITION",
            "message": "يرجى تجهيز بطاقة المشروع للمعرض",

            "exhibition_date": idea.exhibition_date,

            "data": {
                "title": idea.title,
                "image": idea.exhibition_image,
                "project_goal": idea.project_goal,
                "project_services": idea.project_services,

                "owner_email": request.user.email,

                "team": [
                    {
                        "email": m.user.email,
                        "role": m.role
                    }
                    for m in idea.team_members.all()
                ]
            }
        })


#//////////////////////////////// UPDATE EXHIBITION CARD  /////////////////////////////

class UpdateExhibitionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        idea = Idea.objects.get(owner=request.user)

        idea.project_goal = request.data.get("project_goal")
        idea.project_services = request.data.get("project_services")
        idea.owner_email = request.data.get("owner_email")
        idea.team_emails = request.data.get("team_emails")

        if "exhibition_image" in request.FILES:
            idea.exhibition_image = request.FILES["exhibition_image"]

        idea.save()

        return Response({"detail": "تم تحديث بطاقة المشروع"})