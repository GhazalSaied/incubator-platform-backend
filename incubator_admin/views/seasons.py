from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ideas.models import Season
from core.permissions import IsDirector
from incubator_admin.serializers.seasons import SeasonCreateSerializer,SeasonPublishSerializer


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
