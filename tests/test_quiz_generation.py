import json
from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors

from quizzes_app.generation import (
    DEFAULT_MODEL_NAME,
    QuizGenerationError,
    build_prompt,
    generate_quiz,
)

CLIENT_TARGET = 'quizzes_app.generation.genai.Client'
TRANSCRIPT = 'Django is a Python web framework.'
QUIZ_PAYLOAD = {
    'title': 'Django Basics',
    'description': 'A short intro to Django.',
    'questions': [
        {
            'question_title': 'What is Django?',
            'question_options': ['A framework', 'A language', 'A database', 'An IDE'],
            'answer': 'A framework',
        }
    ],
}


@pytest.fixture(autouse=True)
def api_key(monkeypatch):
    """Provide a Gemini API key for every test in this module."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')


def _client_returning(text):
    """Return a mocked Gemini client whose response carries the given text."""
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(text=text)
    return client


def test_generate_quiz_parses_plain_json():
    client = _client_returning(json.dumps(QUIZ_PAYLOAD))

    with patch(CLIENT_TARGET, return_value=client):
        quiz = generate_quiz(TRANSCRIPT)

    assert quiz == QUIZ_PAYLOAD


def test_generate_quiz_accepts_json_code_fences():
    fenced = f'```json\n{json.dumps(QUIZ_PAYLOAD)}\n```'
    client = _client_returning(fenced)

    with patch(CLIENT_TARGET, return_value=client):
        quiz = generate_quiz(TRANSCRIPT)

    assert quiz == QUIZ_PAYLOAD


def test_generate_quiz_accepts_bare_code_fences():
    fenced = f'```\n{json.dumps(QUIZ_PAYLOAD)}\n```'
    client = _client_returning(fenced)

    with patch(CLIENT_TARGET, return_value=client):
        quiz = generate_quiz(TRANSCRIPT)

    assert quiz == QUIZ_PAYLOAD


def test_generate_quiz_ignores_surrounding_whitespace():
    client = _client_returning(f'\n\n  ```json\n{json.dumps(QUIZ_PAYLOAD)}\n```  \n')

    with patch(CLIENT_TARGET, return_value=client):
        quiz = generate_quiz(TRANSCRIPT)

    assert quiz == QUIZ_PAYLOAD


def test_generate_quiz_accepts_unterminated_code_fence():
    client = _client_returning(f'```json\n{json.dumps(QUIZ_PAYLOAD)}')

    with patch(CLIENT_TARGET, return_value=client):
        quiz = generate_quiz(TRANSCRIPT)

    assert quiz == QUIZ_PAYLOAD


def test_generate_quiz_sends_prompt_with_transcript():
    client = _client_returning(json.dumps(QUIZ_PAYLOAD))

    with patch(CLIENT_TARGET, return_value=client):
        generate_quiz(TRANSCRIPT)

    client.models.generate_content.assert_called_once_with(
        model=DEFAULT_MODEL_NAME,
        contents=build_prompt(TRANSCRIPT),
    )


def test_generate_quiz_uses_requested_model():
    client = _client_returning(json.dumps(QUIZ_PAYLOAD))

    with patch(CLIENT_TARGET, return_value=client):
        generate_quiz(TRANSCRIPT, model_name='gemini-2.0-flash-lite')

    kwargs = client.models.generate_content.call_args.kwargs
    assert kwargs['model'] == 'gemini-2.0-flash-lite'


def test_generate_quiz_passes_api_key_to_client():
    client = _client_returning(json.dumps(QUIZ_PAYLOAD))

    with patch(CLIENT_TARGET, return_value=client) as client_class:
        generate_quiz(TRANSCRIPT)

    client_class.assert_called_once_with(api_key='test-key')


def test_generate_quiz_requires_api_key(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY')

    with pytest.raises(QuizGenerationError):
        generate_quiz(TRANSCRIPT)


def test_generate_quiz_rejects_blank_api_key(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', '')

    with pytest.raises(QuizGenerationError):
        generate_quiz(TRANSCRIPT)


def test_generate_quiz_rejects_non_json_response():
    client = _client_returning('Sorry, I cannot help with that.')

    with patch(CLIENT_TARGET, return_value=client):
        with pytest.raises(QuizGenerationError):
            generate_quiz(TRANSCRIPT)


def test_generate_quiz_rejects_json_that_is_not_an_object():
    client = _client_returning('["not", "a", "quiz"]')

    with patch(CLIENT_TARGET, return_value=client):
        with pytest.raises(QuizGenerationError):
            generate_quiz(TRANSCRIPT)


def test_generate_quiz_rejects_empty_response():
    client = _client_returning('')

    with patch(CLIENT_TARGET, return_value=client):
        with pytest.raises(QuizGenerationError):
            generate_quiz(TRANSCRIPT)


def test_generate_quiz_rejects_missing_response_text():
    client = _client_returning(None)

    with patch(CLIENT_TARGET, return_value=client):
        with pytest.raises(QuizGenerationError):
            generate_quiz(TRANSCRIPT)


def test_generate_quiz_wraps_api_errors():
    client = MagicMock()
    client.models.generate_content.side_effect = errors.ClientError(
        429, {'error': {'message': 'rate limited'}}
    )

    with patch(CLIENT_TARGET, return_value=client):
        with pytest.raises(QuizGenerationError):
            generate_quiz(TRANSCRIPT)


def test_build_prompt_appends_transcript_at_the_end():
    prompt = build_prompt(TRANSCRIPT)

    assert prompt.rstrip().endswith(TRANSCRIPT)


def test_build_prompt_states_the_required_structure():
    prompt = build_prompt(TRANSCRIPT)

    assert 'question_options' in prompt
    assert 'exactly 10 questions' in prompt
