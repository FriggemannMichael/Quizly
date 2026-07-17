from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from quizzes_app.audio import AudioExtractionError
from quizzes_app.generation import QuizGenerationError
from quizzes_app.models import Quiz
from quizzes_app.transcription import TranscriptionError

PIPELINE = 'quizzes_app.pipeline'
VIDEO_URL = 'https://youtu.be/dQw4w9WgXcQ'
NORMALIZED_URL = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
TRANSCRIPT = 'Django is a Python web framework.'
AUDIO_PATH = Path('/tmp/dQw4w9WgXcQ.mp3')
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


def _question(number: int) -> dict:
    """Return one generated question in the shape the validator expects."""
    return {
        'question_title': f'Question {number}?',
        'question_options': [f'Option {number}{letter}' for letter in 'ABCD'],
        'answer': f'Option {number}A',
    }


def _quiz_payload(question_count: int = 10) -> dict:
    """Return a generated quiz payload with the given number of questions."""
    return {
        'title': 'Django Basics',
        'description': 'A short intro to Django.',
        'questions': [_question(number) for number in range(1, question_count + 1)],
    }


@contextmanager
def _fake_extract_audio(video_url: str):
    """Stand in for yt-dlp by yielding a fixed audio path."""
    yield AUDIO_PATH


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username='quiz_user',
        email='quiz-user@example.com',
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


@contextmanager
def _mocked_pipeline(payload=None, audio=_fake_extract_audio, **overrides):
    """Replace the external services the pipeline calls with fakes."""
    transcribe = overrides.get('transcribe', {'return_value': TRANSCRIPT})
    generate = overrides.get('generate', {'return_value': payload or _quiz_payload()})
    with (
        patch(f'{PIPELINE}.extract_audio', audio),
        patch(f'{PIPELINE}.transcribe_audio', **transcribe) as transcribe_mock,
        patch(f'{PIPELINE}.generate_quiz', **generate) as generate_mock,
    ):
        yield transcribe_mock, generate_mock


def _post(client, url=VIDEO_URL):
    """Send a quiz creation request with the given video URL."""
    return client.post(reverse('quiz-list'), {'url': url}, format='json')


def test_quiz_list_url_is_registered():
    assert reverse('quiz-list') == '/api/quizzes/'


@pytest.mark.django_db
def test_create_quiz_requires_authentication(api_client):
    with _mocked_pipeline():
        response = _post(api_client)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Quiz.objects.count() == 0


@pytest.mark.django_db
def test_create_quiz_returns_the_documented_quiz_object(auth_client):
    with _mocked_pipeline():
        response = _post(auth_client)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert set(body) == QUIZ_FIELDS
    assert body['title'] == 'Django Basics'
    assert body['description'] == 'A short intro to Django.'
    assert body['video_url'] == NORMALIZED_URL
    assert len(body['questions']) == 10
    assert set(body['questions'][0]) == QUESTION_FIELDS
    assert body['questions'][0]['question_title'] == 'Question 1?'
    assert body['questions'][0]['answer'] == 'Option 1A'
    assert body['questions'][0]['question_options'] == [
        'Option 1A',
        'Option 1B',
        'Option 1C',
        'Option 1D',
    ]


@pytest.mark.django_db
def test_create_quiz_saves_quiz_and_questions_for_the_current_user(auth_client, user):
    with _mocked_pipeline():
        response = _post(auth_client)

    quiz = Quiz.objects.get(pk=response.json()['id'])
    assert quiz.owner == user
    assert quiz.title == 'Django Basics'
    assert quiz.video_url == NORMALIZED_URL
    assert quiz.questions.count() == 10


@pytest.mark.django_db
def test_create_quiz_normalizes_the_video_url_before_extracting_audio(auth_client):
    seen = []

    @contextmanager
    def recording_extract_audio(video_url: str):
        seen.append(video_url)
        yield AUDIO_PATH

    with _mocked_pipeline(audio=recording_extract_audio):
        _post(auth_client, url='https://m.youtube.com/watch?v=dQw4w9WgXcQ&t=42')

    assert seen == [NORMALIZED_URL]


@pytest.mark.django_db
def test_create_quiz_feeds_the_transcript_into_generation(auth_client):
    with _mocked_pipeline() as (transcribe, generate):
        _post(auth_client)

    transcribe.assert_called_once_with(AUDIO_PATH)
    generate.assert_called_once_with(TRANSCRIPT)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    [
        'https://vimeo.com/123456789',
        'https://www.youtube.com/watch?v=short',
        'not-a-url',
        '',
    ],
)
def test_create_quiz_rejects_invalid_urls(auth_client, url):
    with _mocked_pipeline():
        response = _post(auth_client, url=url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Quiz.objects.count() == 0


@pytest.mark.django_db
def test_create_quiz_rejects_playlist_urls(auth_client):
    with _mocked_pipeline():
        response = _post(
            auth_client,
            url='https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123',
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Quiz.objects.count() == 0


@pytest.mark.django_db
def test_create_quiz_requires_the_url_field(auth_client):
    with _mocked_pipeline():
        response = auth_client.post(reverse('quiz-list'), {}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'url' in response.json()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('service', 'error'),
    [
        ('transcribe', TranscriptionError('whisper failed')),
        ('generate', QuizGenerationError('gemini failed')),
    ],
)
def test_create_quiz_reports_pipeline_failures(auth_client, service, error):
    with _mocked_pipeline(**{service: {'side_effect': error}}):
        response = _post(auth_client)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'detail' in response.json()
    assert Quiz.objects.count() == 0


@pytest.mark.django_db
def test_create_quiz_reports_audio_extraction_failure(auth_client):
    @contextmanager
    def failing_extract_audio(video_url: str):
        raise AudioExtractionError('yt-dlp failed')
        yield  # pragma: no cover

    with _mocked_pipeline(audio=failing_extract_audio):
        response = _post(auth_client)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert Quiz.objects.count() == 0


@pytest.mark.django_db
def test_create_quiz_reports_a_quiz_that_fails_validation(auth_client):
    with _mocked_pipeline(payload=_quiz_payload(question_count=3)):
        response = _post(auth_client)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert Quiz.objects.count() == 0
