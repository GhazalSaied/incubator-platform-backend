from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from ideas.models import FormQuestion, FormQuestionChoice
from incubator_admin.serializers.form_choice import FormQuestionChoiceSerializer
from core.permissions import IsAdminOrSecretary


class FormQuestionChoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = FormQuestionChoiceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        return FormQuestionChoice.objects.filter(
            question_id=question_id
        ).order_by('order')

    def perform_create(self, serializer):
        question_id = self.kwargs['question_id']
        question = get_object_or_404(FormQuestion, id=question_id)
        
        if question.type not in [
           FormQuestion.SELECT,
           FormQuestion.SELECT_MULTIPLE
        ]:
           raise ValidationError({
               "detail": "لا يمكن إضافة خيارات إلا للأسئلة من نوع select أو select_multiple"
            })


        serializer.save(question=question)


class FormQuestionChoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FormQuestionChoiceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    lookup_url_kwarg = "choice_id"

    def get_queryset(self):
        question_id = self.kwargs["question_id"]
        return FormQuestionChoice.objects.filter(
            question_id=question_id
        )