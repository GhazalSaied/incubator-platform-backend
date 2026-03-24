from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from ideas.models import Season
from core.permissions import IsDirector
from incubator_admin.serializers.seasons import SeasonCreateSerializer,SeasonPublishSerializer,SeasonSerializer
from rest_framework.generics import RetrieveUpdateAPIView

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
            return Response(
                {"detail": "الموسم غير موجود"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not season.is_open:
            return Response(
                {"detail": "الموسم مغلق بالفعل"},
                status=status.HTTP_400_BAD_REQUEST
            )

        season.is_open = False
        season.save()

        return Response(
            {"detail": "تم إغلاق الموسم بنجاح"},
            status=status.HTTP_200_OK
        )




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
    permission_classes = [IsAuthenticated, IsDirector ]
    lookup_url_kwarg = "season_id"

    def get_queryset(self):
        return Season.objects.all()
    

   
   
   