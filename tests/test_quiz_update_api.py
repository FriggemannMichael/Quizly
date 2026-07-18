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
        username='update_user',
        email='update-user@example.com',
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


def _update(client, quiz_id, payload):
    """Send a quiz partial update request for the given quiz id."""
    return client.patch(reverse('quiz-detail', args=[quiz_id]), payload, format='json')


@pytest.mark.django_db
def test_update_requires_authentication(api_client, user):
    quiz = _create_quiz(user)

    response = _update(api_client, quiz.id, {'title': 'New Title'})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_changes_only_the_submitted_fields(auth_client, user):
    quiz = _create_quiz(user)

    response = _update(auth_client, quiz.id, {'title': 'Partially Updated Title'})

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert set(body) == QUIZ_FIELDS
    assert body['title'] == 'Partially Updated Title'
    assert body['description'] == quiz.description
    quiz.refresh_from_db()
    assert quiz.title == 'Partially Updated Title'


@pytest.mark.django_db
def test_update_changes_title_and_description(auth_client, user):
    quiz = _create_quiz(user)

    response = _update(
        auth_client,
        quiz.id,
        {
            'title': 'Partially Updated Title',
            'description': 'Partially Updated Description',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    quiz.refresh_from_db()
    assert quiz.title == 'Partially Updated Title'
    assert quiz.description == 'Partially Updated Description'


@pytest.mark.django_db
def test_update_ignores_the_video_url_field(auth_client, user):
    quiz = _create_quiz(user)
    original_video_url = quiz.video_url

    response = _update(auth_client, quiz.id, {'video_url': 'https://example.com/other'})

    assert response.status_code == status.HTTP_200_OK
    quiz.refresh_from_db()
    assert quiz.video_url == original_video_url


@pytest.mark.django_db
def test_update_rejects_a_blank_title(auth_client, user):
    quiz = _create_quiz(user)

    response = _update(auth_client, quiz.id, {'title': ''})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    quiz.refresh_from_db()
    assert quiz.title == 'Django Basics'


@pytest.mark.django_db
def test_update_forbids_another_users_quiz(auth_client, other_user):
    quiz = _create_quiz(other_user, title='Theirs')

    response = _update(auth_client, quiz.id, {'title': 'Hijacked'})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    quiz.refresh_from_db()
    assert quiz.title == 'Theirs'


@pytest.mark.django_db
def test_update_returns_404_for_a_missing_quiz(auth_client):
    response = _update(auth_client, 999999, {'title': 'New Title'})

    assert response.status_code == status.HTTP_404_NOT_FOUND
