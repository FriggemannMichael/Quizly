from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import NoReverseMatch, reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.cookies import ACCESS_TOKEN_COOKIE_NAME

PIPELINE = 'quizzes_app.pipeline'
VIDEO_URL = 'https://youtu.be/dQw4w9WgXcQ'
AUDIO_PATH = Path('/tmp/dQw4w9WgXcQ.mp3')
PASSWORD = 'Str0ng-test-pass!'


def _quiz_payload() -> dict:
    """Return a generated quiz payload that passes structure validation."""
    return {
        'title': 'Django Basics',
        'description': 'A short intro to Django.',
        'questions': [
            {
                'question_title': f'Question {number}?',
                'question_options': [f'Option {number}{x}' for x in 'ABCD'],
                'answer': f'Option {number}A',
            }
            for number in range(1, 11)
        ],
    }


@contextmanager
def _fake_extract_audio(video_url: str):
    """Stand in for yt-dlp by yielding a fixed audio path."""
    yield AUDIO_PATH


@contextmanager
def _mocked_pipeline():
    """Replace the external services so only authentication is exercised."""
    with (
        patch(f'{PIPELINE}.extract_audio', _fake_extract_audio),
        patch(f'{PIPELINE}.transcribe_audio', return_value='A transcript.'),
        patch(f'{PIPELINE}.generate_quiz', return_value=_quiz_payload()),
    ):
        yield


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username='cookie_user',
        email='cookie-user@example.com',
        password=PASSWORD,
    )


@pytest.fixture
def api_client():
    return APIClient()


def _login(client, user) -> None:
    """Log in through the real endpoint so the client holds auth cookies."""
    response = client.post(
        reverse('login'),
        {'username': user.username, 'password': PASSWORD},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert ACCESS_TOKEN_COOKIE_NAME in response.cookies


def _create_quiz(client):
    """Post a quiz creation request with the pipeline mocked out."""
    with _mocked_pipeline():
        return client.post(reverse('quiz-list'), {'url': VIDEO_URL}, format='json')


@pytest.mark.django_db
def test_login_cookies_authenticate_a_protected_request(api_client, user):
    _login(api_client, user)

    response = _create_quiz(api_client)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_access_token_cookie_authenticates_a_protected_request(api_client, user):
    access_token = RefreshToken.for_user(user).access_token
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = str(access_token)

    response = _create_quiz(api_client)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_protected_request_without_any_credentials_is_rejected(api_client):
    response = _create_quiz(api_client)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_invalid_access_token_cookie_is_rejected(api_client):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = 'not-a-jwt'

    response = _create_quiz(api_client)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authorization_header_still_authenticates(api_client, user):
    access_token = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = _create_quiz(api_client)

    assert response.status_code == status.HTTP_201_CREATED


def test_stock_token_obtain_route_is_removed():
    with pytest.raises(NoReverseMatch):
        reverse('token_obtain_pair')
