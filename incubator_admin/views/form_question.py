from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from ideas.models import FormQuestion, IdeaForm
from incubator_admin.serializers.form_question import FormQuestionSerializer
from core.permissions import IsAdminOrSecretary


class FormQuestionListCreateView(ListCreateAPIView):
    serializer_class = FormQuestionSerializer
    permission_classes = [IsAdminOrSecretary]

    def get_queryset(self):
        form_id = self.kwargs['form_id']
        return FormQuestion.objects.filter(form_id=form_id).order_by('order')

    def perform_create(self, serializer):
        form_id = self.kwargs['form_id']
        form = IdeaForm.objects.get(id=form_id)
        serializer.save(form=form)
