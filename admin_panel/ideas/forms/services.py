from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from ideas.models import IdeaForm, FormQuestion, FormQuestionChoice


def create_form(serializer):
    return serializer.save()


def get_form_questions(form_id):
    return FormQuestion.objects.filter(form_id=form_id).order_by("order")


def create_form_question(serializer, form_id):
    form = get_object_or_404(IdeaForm, id=form_id)
    return serializer.save(form=form)


def get_question_queryset(form_id):
    return FormQuestion.objects.filter(form_id=form_id)


def get_question_choices(question_id):
    return FormQuestionChoice.objects.filter(
        question_id=question_id
    ).order_by("order")


def create_question_choice(serializer, question_id):
    question = get_object_or_404(FormQuestion, id=question_id)

    if question.type not in [
        FormQuestion.SELECT,
        FormQuestion.SELECT_MULTIPLE
    ]:
        raise ValidationError({
            "detail": "لا يمكن إضافة خيارات إلا للأسئلة من نوع select"
        })

    return serializer.save(question=question)


def get_choice_queryset(question_id):
    return FormQuestionChoice.objects.filter(question_id=question_id)