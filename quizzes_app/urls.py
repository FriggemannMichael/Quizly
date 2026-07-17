from django.urls import path

from quizzes_app.views import QuizListCreateView

urlpatterns = [
    path('quizzes/', QuizListCreateView.as_view(), name='quiz-list'),
]
