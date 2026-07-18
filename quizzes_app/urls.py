from django.urls import path

from quizzes_app.views import QuizDetailView, QuizListCreateView

urlpatterns = [
    path('quizzes/', QuizListCreateView.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
]
