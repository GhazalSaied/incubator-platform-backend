from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Idea, Season , IdeaStatus
from .serializers import (
    IdeaFormSerializer,
    IdeaCreateUpdateSerializer,
    IdeaDetailSerializer
)
from notifications.models import Notification
from ideas.services.idea_validation import IdeaFormValidator

#///////////////////////////GET CUURENT IDEA FORM SERIALIZER /////////////////////////////////

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
    permission_classes = [IsAuthenticated]

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
        try:
            idea = Idea.objects.get(id=idea_id, owner=request.user)
        except Idea.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not idea.can_be_edited():
            return Response(
                {"detail": "لا يمكن تعديل الفكرة في هذه المرحلة"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = IdeaCreateUpdateSerializer(
            idea,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(IdeaDetailSerializer(idea).data)

 #////////////////////////  WITHDRIDEAVIEW //////////////////////////////////////////

class WithdrawIdeaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, idea_id):
        try:
            idea = Idea.objects.get(id=idea_id, owner=request.user)
        except Idea.DoesNotExist:
            return Response(
                {"detail": "الفكرة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )

        if idea.status not in [
            IdeaStatus.DRAFT,
            IdeaStatus.SUBMITTED
        ]:
            return Response(
                {"detail": "لا يمكن سحب الفكرة في هذه المرحلة"},
                status=status.HTTP_400_BAD_REQUEST
            )

        idea.status = IdeaStatus.WITHDRAWN
        idea.save()

        return Response(
            {"detail": "تم سحب الفكرة بنجاح"},
            status=status.HTTP_200_OK
        )
