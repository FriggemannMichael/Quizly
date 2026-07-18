import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model

from quizzes_app.admin import QuestionAdmin, QuizAdmin
from quizzes_app.models import Question, Quiz


@pytest.fixture
def admin_request(db, rf):
    """Return an admin request issued by a superuser."""
    request = rf.get('/admin/')
    request.user = get_user_model().objects.create_superuser(
        username='admin_user',
        email='admin-user@example.com',
        password='Str0ng-test-pass!',
    )
    return request


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


def test_quiz_and_question_admin_allow_editing(admin_request):
    for model in (Quiz, Question):
        model_admin = admin.site._registry[model]

        assert model_admin.has_change_permission(admin_request) is True


def test_quiz_and_question_admin_block_add_and_delete(admin_request):
    for model in (Quiz, Question):
        model_admin = admin.site._registry[model]

        assert model_admin.has_add_permission(admin_request) is False
        assert model_admin.has_delete_permission(admin_request) is False


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
