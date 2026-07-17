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


def _create_quiz(owner, title: str) -> Quiz:
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
        username='list_user',
        email='list-user@example.com',
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


def _list(client):
    """Send a quiz list request."""
    return client.get(reverse('quiz-list'))


@pytest.mark.django_db
def test_list_requires_authentication(api_client):
    response = _list(api_client)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_returns_an_empty_array_when_user_has_no_quizzes(auth_client):
    response = _list(auth_client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.django_db
def test_list_returns_the_documented_quiz_shape(auth_client, user):
    _create_quiz(user, 'Django Basics')

    response = _list(auth_client)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert set(body[0]) == QUIZ_FIELDS
    assert set(body[0]['questions'][0]) == QUESTION_FIELDS


@pytest.mark.django_db
def test_list_returns_only_the_current_users_quizzes(auth_client, user, other_user):
    _create_quiz(user, 'Mine')
    _create_quiz(other_user, 'Theirs')

    response = _list(auth_client)

    titles = [quiz['title'] for quiz in response.json()]
    assert titles == ['Mine']


@pytest.mark.django_db
def test_list_orders_newest_first(auth_client, user):
    _create_quiz(user, 'Older')
    _create_quiz(user, 'Newer')

    response = _list(auth_client)

    titles = [quiz['title'] for quiz in response.json()]
    assert titles == ['Newer', 'Older']
