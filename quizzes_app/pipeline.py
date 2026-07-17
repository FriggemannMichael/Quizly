from django.db import transaction

from quizzes_app.audio import extract_audio
from quizzes_app.generation import generate_quiz
from quizzes_app.models import Question, Quiz
from quizzes_app.transcription import transcribe_audio
from quizzes_app.validation import validate_quiz_payload


def generate_quiz_payload(video_url: str) -> dict:
    """Return a validated quiz payload for an already normalized video URL.

    Every step here reaches out to a slow external service, so callers should
    keep this out of any open database transaction.
    """
    with extract_audio(video_url) as audio_path:
        transcript = transcribe_audio(audio_path)
    return validate_quiz_payload(generate_quiz(transcript))


@transaction.atomic
def save_quiz(owner, video_url: str, payload: dict) -> Quiz:
    """Persist a validated quiz payload and its questions for the owner."""
    quiz = Quiz.objects.create(
        owner=owner,
        title=payload['title'],
        description=payload['description'],
        video_url=video_url,
    )
    Question.objects.bulk_create(_unsaved_questions(quiz, payload['questions']))
    return quiz


def _unsaved_questions(quiz: Quiz, questions: list) -> list[Question]:
    """Build the unsaved Question rows for a validated quiz payload."""
    return [
        Question(
            quiz=quiz,
            question_title=question['question_title'],
            question_options=question['question_options'],
            answer=question['answer'],
        )
        for question in questions
    ]
