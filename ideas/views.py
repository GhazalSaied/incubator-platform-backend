from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Idea, Season
from .serializers import (
    IdeaFormSerializer,
    IdeaCreateUpdateSerializer,
    IdeaDetailSerializer
)
from notifications.models import Notification

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
        season = Season.objects.filter(is_open=True).first()
        if not season:
            return Response(
                {"detail": "التقديم مغلق حالياً"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = IdeaCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idea = serializer.save(
            owner=request.user,
            season=season,
            status='SUBMITTED'
        )

        
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

