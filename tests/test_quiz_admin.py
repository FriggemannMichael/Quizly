from django.contrib import admin

from quizzes.admin import QuestionAdmin, QuizAdmin
from quizzes.models import Question, Quiz


def test_quiz_and_question_models_are_registered_in_admin():
    assert isinstance(admin.site._registry[Quiz], QuizAdmin)
    assert isinstance(admin.site._registry[Question], QuestionAdmin)


def test_quiz_admin_exposes_useful_review_fields():
    model_admin = admin.site._registry[Quiz]

    assert model_admin.list_display == (
        'title',
        'owner',
        'video_url',
        'created_at',
        'updated_at',
    )
    assert model_admin.search_fields == ('title', 'description', 'video_url')
    assert model_admin.list_filter == ('created_at', 'updated_at')


def test_question_admin_exposes_useful_review_fields():
    model_admin = admin.site._registry[Question]

    assert model_admin.list_display == (
        'question_title',
        'quiz',
        'answer',
        'created_at',
        'updated_at',
    )
    assert model_admin.search_fields == ('question_title', 'answer', 'quiz__title')
    assert model_admin.list_filter == ('created_at', 'updated_at')
