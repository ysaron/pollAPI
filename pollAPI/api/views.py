from rest_framework import generics, permissions
from django.db.models import Q, Count, F

from .models import Poll
from .serializers import PollListSerializer, PollDetailSerializer, AnswerCreateSerializer, MyPollsListSerializer


class PollListView(generics.ListAPIView):
    """ Вывод списка активных опросов """

    serializer_class = PollListSerializer

    def get_queryset(self):
        return Poll.objects.active()


class PollDetailView(generics.RetrieveAPIView):
    """ Вывод опроса со всеми связанными вопросами """

    serializer_class = PollDetailSerializer

    def get_queryset(self):
        return Poll.objects.active()


class AnswerCreateView(generics.CreateAPIView):
    """ Предоставление ответа """
    serializer_class = AnswerCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyPollsListView(generics.ListAPIView):
    serializer_class = MyPollsListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Poll.objects.active().annotate(
            num_questions=Count('question'),
            num_user_answers=Count('question__answer', filter=Q(question__answer__user=self.request.user)),
        ).filter(
            num_questions=F('num_user_answers')
        ).exclude(
            num_questions=0,
        )
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
