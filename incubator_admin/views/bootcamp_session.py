from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from bootcamp.models import BootcampSession
from incubator_admin.serializers.bootcamp_session import BootcampSessionSerializer
from core.permissions import IsAdminOrSecretary


class BootcampSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = BootcampSessionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get_queryset(self):
        phase_id = self.request.query_params.get("phase")

        queryset = BootcampSession.objects.all()

        if phase_id:
            queryset = queryset.filter(phase_id=phase_id)

        return queryset.order_by("start_time")


class BootcampSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BootcampSessionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    queryset = BootcampSession.objects.all()