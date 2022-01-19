from django.urls import path
from . import views


urlpatterns = [
    path('active_polls/', views.PollListView.as_view()),
    path('active_polls/<int:pk>/', views.PollDetailView.as_view()),
    path('answer/', views.AnswerCreateView.as_view()),
    path('my_polls/', views.MyPollsListView.as_view()),
]
