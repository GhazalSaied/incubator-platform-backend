from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from ideas.models import Season,Idea,IdeaStatus
from core.permissions import IsDirector
from incubator_admin.serializers.seasons import SeasonCreateSerializer,SeasonPublishSerializer,SeasonSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.exceptions import PermissionDenied
from ideas.services.season_phase_service import SeasonPhaseService
from ideas.phases import SeasonPhase

class SeasonCreateView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsDirector
    ]

    def post(self, request):
        serializer = SeasonCreateSerializer(data=request.data)

        if serializer.is_valid():
            season = serializer.save()
            return Response(
                SeasonCreateSerializer(season).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class SeasonPublishView(APIView):
    permission_classes = [IsDirector]

    def post(self, request, pk):
        season = Season.objects.get(pk=pk)

        serializer = SeasonPublishSerializer(
            instance=season,
            data={},              # 👈 مهم جداً
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "تم نشر الموسم بنجاح"},
            status=status.HTTP_200_OK
        )



class CloseSeasonAPIView(APIView):
    permission_classes = [IsDirector]

    def post(self, request, season_id):
        try:
            season = Season.objects.get(id=season_id)
        except Season.DoesNotExist:
            return Response({"detail": "Season not found"}, status=404)

        if not season.is_open:
            return Response({"detail": "الموسم مغلق بالفعل"}, status=400)

        # 🔒 إغلاق الموسم
        season.is_open = False
        season.save()

        # 🔥 نقل الأفكار إلى UNDER_REVIEW (مو bootcamp!)
        Idea.objects.filter(
            season=season,
            status=IdeaStatus.SUBMITTED
        ).update(status=IdeaStatus.UNDER_REVIEW)

        return Response({
            "detail": "تم إغلاق الموسم وبدء مرحلة المعسكر"
        })



class SeasonListAPIView(ListAPIView):
    serializer_class = SeasonSerializer
    permission_classes = [IsAuthenticated, IsDirector]

    def get_queryset(self):
        return Season.objects.all().order_by('-id')
    
class SeasonListAPIView(ListAPIView):
    serializer_class = SeasonSerializer
    permission_classes = [IsAuthenticated, IsDirector]

    def get_queryset(self):
        return Season.objects.all().order_by('-id')
    
    
    


class SeasonDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = SeasonSerializer
    permission_classes = [IsAuthenticated, IsDirector]
    lookup_url_kwarg = "season_id"

    def get_queryset(self):
        return Season.objects.all()

    def update(self, request, *args, **kwargs):

        # 🔥 تحقق من المرحلة
        if not SeasonPhaseService.is_phase(SeasonPhase.SUBMISSION):
            raise PermissionDenied("يمكن تعديل الموسم فقط خلال مرحلة التقديم")

        return super().update(request, *args, **kwargs)
    

   
   
   