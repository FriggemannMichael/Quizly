import json
import os

from google import genai
from google.genai import errors

from quizzes_app.prompts import QUIZ_PROMPT_TEMPLATE

DEFAULT_MODEL_NAME = 'gemini-3.5-flash'


class QuizGenerationError(Exception):
    """Raised when Gemini cannot produce a usable quiz."""


def generate_quiz(transcript: str, model_name: str = DEFAULT_MODEL_NAME) -> dict:
    """Return the quiz payload Gemini generated for a transcript."""
    client = _build_client()
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=build_prompt(transcript),
        )
    except errors.APIError as error:
        raise QuizGenerationError(str(error)) from error
    return _parse_quiz(response.text)


def build_prompt(transcript: str) -> str:
    """Return the Gemini prompt with the transcript appended at the end."""
    return f'{QUIZ_PROMPT_TEMPLATE}{transcript}'


def _build_client() -> genai.Client:
    """Return a Gemini client configured from the environment."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise QuizGenerationError('GEMINI_API_KEY is not configured.')
    return genai.Client(api_key=api_key)


def _parse_quiz(text: str | None) -> dict:
    """Return the quiz object parsed from a raw Gemini response."""
    if not text or not text.strip():
        raise QuizGenerationError('Gemini returned an empty response.')
    try:
        payload = json.loads(_strip_code_fences(text))
    except json.JSONDecodeError as error:
        raise QuizGenerationError('Gemini returned invalid JSON.') from error
    if not isinstance(payload, dict):
        raise QuizGenerationError('Gemini returned JSON that is not an object.')
    return payload


def _strip_code_fences(text: str) -> str:
    """Return the response body without a surrounding Markdown code fence."""
    cleaned = text.strip()
    if not cleaned.startswith('```'):
        return cleaned
    lines = cleaned.splitlines()[1:]
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]
    return '\n'.join(lines).strip()
