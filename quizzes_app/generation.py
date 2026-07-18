import json
import os

from google import genai
from google.genai import errors
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from quizzes_app.prompts import QUIZ_PROMPT_TEMPLATE

DEFAULT_MODEL_NAME = 'gemini-3.5-flash'
MAX_ATTEMPTS = 3


class QuizGenerationError(Exception):
    """Raised when Gemini cannot produce a usable quiz."""


def generate_quiz(transcript: str, model_name: str = DEFAULT_MODEL_NAME) -> dict:
    """Return the quiz payload Gemini generated for a transcript."""
    client = _build_client()
    try:
        response = _request_quiz(client, model_name, build_prompt(transcript))
    except errors.APIError as error:
        raise QuizGenerationError(str(error)) from error
    return _parse_quiz(response.text)


def _is_transient(error: BaseException) -> bool:
    """Return whether the error is a temporary condition worth retrying."""
    if not isinstance(error, errors.APIError):
        return False
    if error.code == 503:
        return True
    if error.code != 429:
        return False
    return _reports_retry_delay(error) and not _reports_zero_quota(error)


def _reports_retry_delay(error: errors.APIError) -> bool:
    """Return whether the API asked the caller to retry after a delay."""
    return any(entry.get('retryDelay') for entry in _error_details(error))


def _reports_zero_quota(error: errors.APIError) -> bool:
    """Return whether a quota of zero makes retrying pointless."""
    return any(
        violation.get('quotaValue') == '0'
        for entry in _error_details(error)
        for violation in entry.get('violations', [])
    )


def _error_details(error: errors.APIError) -> list[dict]:
    """Return the structured detail entries of a Gemini error response."""
    if not isinstance(error.details, dict):
        return []
    inner = error.details.get('error')
    if not isinstance(inner, dict):
        return []
    return [entry for entry in inner.get('details', []) if isinstance(entry, dict)]


@retry(
    retry=retry_if_exception(_is_transient),
    stop=stop_after_attempt(MAX_ATTEMPTS),
    wait=wait_exponential(multiplier=1, max=8),
    reraise=True,
)
def _request_quiz(client: genai.Client, model_name: str, prompt: str):
    """Call Gemini, retrying transient availability errors with backoff."""
    return client.models.generate_content(model=model_name, contents=prompt)


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
