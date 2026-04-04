from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from ideas.serializers import IdeaFormSerializer, FormQuestionSerializer,FormQuestionChoiceSerializer
from core.permissions import IsAdminOrSecretary
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from admin_panel.ideas.forms.services import create_form, get_form_questions,create_form_question,get_question_queryset,get_question_choices,create_question_choice, get_choice_queryset
from rest_framework import generics
#\\\\creat form\\\
class IdeaFormCreateView(APIView):
    permission_classes = [IsAdminOrSecretary]

    def post(self, request):
        serializer = IdeaFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        form = create_form(serializer)

        return Response(form.data if hasattr(form, "data") else serializer.data, status=status.HTTP_201_CREATED)
    
    
    
#\\\\\\FormQuestionListCreate\\\\\

class FormQuestionListCreateView(ListCreateAPIView):
    serializer_class = FormQuestionSerializer
    permission_classes = [IsAdminOrSecretary]

    def get_queryset(self):
        return get_form_questions(self.kwargs["form_id"])

    def perform_create(self, serializer):
        create_form_question(serializer, self.kwargs["form_id"])
        
        

#\\\\\\FormQuestionDetail\\\\

class FormQuestionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = FormQuestionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]
    lookup_url_kwarg = "question_id"

    def get_queryset(self):
        return get_question_queryset(self.kwargs["form_id"])
    
    
#\\\\\\FormQuestionChoiceListCreate\\\\

class FormQuestionChoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = FormQuestionChoiceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSecretary]

    def get_queryset(self):
        return get_question_choices(self.kwargs["question_id"])

    def perform_create(self, serializer):
        create_question_choice(serializer, self.kwargs["question_id"])
        
        
#\\\\\\\\\FormQuestionChoiceDetail\\\\\

class FormQuestionChoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FormQuestionChoiceSerializer
    permission_classes = [IsAdminOrSecretary]
    lookup_url_kwarg = "choice_id"

    def get_queryset(self):
        return get_choice_queryset(self.kwargs["question_id"])