import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from quizzes_app.models import Question, Quiz

QUIZ_FIELDS = {
    'id',
    'title',
    'description',
    'created_at',
    'updated_at',
    'video_url',
    'questions',
}
QUESTION_FIELDS = {
    'id',
    'question_title',
    'question_options',
    'answer',
    'created_at',
    'updated_at',
}


def _create_quiz(owner, title: str = 'Django Basics') -> Quiz:
    """Persist a quiz with one question for the given owner."""
    quiz = Quiz.objects.create(
        owner=owner,
        title=title,
        description=f'{title} description.',
        video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    )
    Question.objects.create(
        quiz=quiz,
        question_title='Question 1?',
        question_options=['Option A', 'Option B', 'Option C', 'Option D'],
        answer='Option A',
    )
    return quiz


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username='detail_user',
        email='detail-user@example.com',
        password='Str0ng-test-pass!',
    )


@pytest.fixture
def other_user(db):
    return get_user_model().objects.create_user(
        username='other_user',
        email='other-user@example.com',
        password='Str0ng-test-pass!',
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _detail(client, quiz_id):
    """Send a quiz detail request for the given quiz id."""
    return client.get(reverse('quiz-detail', args=[quiz_id]))


@pytest.mark.django_db
def test_detail_requires_authentication(api_client, user):
    quiz = _create_quiz(user)

    response = _detail(api_client, quiz.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_detail_returns_the_owned_quiz(auth_client, user):
    quiz = _create_quiz(user)

    response = _detail(auth_client, quiz.id)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body['id'] == quiz.id
    assert set(body) == QUIZ_FIELDS
    assert set(body['questions'][0]) == QUESTION_FIELDS


@pytest.mark.django_db
def test_detail_forbids_another_users_quiz(auth_client, other_user):
    quiz = _create_quiz(other_user, title='Theirs')

    response = _detail(auth_client, quiz.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_detail_returns_404_for_a_missing_quiz(auth_client):
    response = _detail(auth_client, 999999)

    assert response.status_code == status.HTTP_404_NOT_FOUND
