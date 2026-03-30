from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ideas.phases import get_current_phase
from bootcamp.models import BootcampSession
from incubator_admin.serializers.bootcamp_session import BootcampSessionSerializer,BootcampAttendanceSerializer
from rest_framework.generics import ListAPIView
from ideas.models import Idea


class BootcampSessionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BootcampSessionSerializer(data=request.data)

        if serializer.is_valid():
            
            # 🔥 ناخد الموسم من البيانات قبل الحفظ
            season = serializer.validated_data.get('season')

            # 🔥 تحقق من المرحلة
            phase = get_current_phase(season)

            if not phase or phase.phase != 'bootcamp':
                return Response(
                    {"detail": "ليس وقت المعسكر"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ إذا تمام → نحفظ
            session = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminBootcampSessionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BootcampSessionSerializer

    def get_queryset(self):
        queryset = BootcampSession.objects.select_related(
            'phase',
            'phase__season',
            'trainer'
        )
        
       
        # 🔹 فلترة حسب الموسم
        season_id = self.request.query_params.get('season_id')
        if season_id:
            queryset = queryset.filter(phase__season_id=season_id)

        

        # 🔹 بحث بالعنوان (لواجهة الادمن)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(location__icontains=search)
            )

        # 🔹 ترتيب
        return queryset.order_by('start_time')
    
    
    



