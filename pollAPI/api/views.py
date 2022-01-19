from rest_framework import generics, permissions
from django.db.models import Q, Count, F

from .models import Poll
from .serializers import PollListSerializer, PollDetailSerializer, AnswerCreateSerializer, MyPollsListSerializer


class PollListView(generics.ListAPIView):
    """ Listing active polls """

    serializer_class = PollListSerializer

    def get_queryset(self):
        return Poll.objects.active()


class PollDetailView(generics.RetrieveAPIView):
    """ Show the poll with all related questions """

    serializer_class = PollDetailSerializer

    def get_queryset(self):
        return Poll.objects.active()


class AnswerCreateView(generics.CreateAPIView):
    """ Providing an answer """
    serializer_class = AnswerCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyPollsListView(generics.ListAPIView):
    """ Displaying a report on the polls completed by the current user """

    serializer_class = MyPollsListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Getting polls where all questions have answers given by the current user
        qs = Poll.objects.annotate(
            num_questions=Count('question'),
            num_user_answers=Count('question__answer', filter=Q(question__answer__user=self.request.user)),
        ).filter(
            num_questions=F('num_user_answers')
        ).exclude(
            num_questions=0,
        )
        return qs

    def get_serializer_context(self):
        """ Passing request to the serializer """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
