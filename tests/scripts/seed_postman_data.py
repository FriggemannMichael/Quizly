"""Seed the user and quiz the Postman API smoke collection relies on.

The collection cannot create a quiz through `POST /api/quizzes/` because that
would run the real yt-dlp/Whisper/Gemini pipeline, so CI seeds one directly.
Safe to run repeatedly: the user is reused and the quiz recreated if missing.
"""

import os
import sys
from pathlib import Path

import django

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SMOKE_USERNAME = 'postman_smoke'
SMOKE_PASSWORD = 'Postman-Sm0ke-2026!'


def main() -> None:
    """Create the smoke user with one ready-made quiz and question."""
    sys.path.insert(0, str(PROJECT_ROOT))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    _ensure_quiz(_ensure_user())


def _ensure_user():
    """Return the smoke user, creating it and refreshing its password."""
    from django.contrib.auth import get_user_model

    user, _ = get_user_model().objects.get_or_create(
        username=SMOKE_USERNAME,
        defaults={'email': 'postman-smoke@example.com'},
    )
    user.set_password(SMOKE_PASSWORD)
    user.save()
    return user


def _ensure_quiz(user) -> None:
    """Attach the smoke quiz with one question to the given user."""
    from quizzes_app.models import Question, Quiz

    quiz, created = Quiz.objects.get_or_create(
        owner=user,
        title='Postman Smoke Quiz',
        defaults={
            'description': 'Seeded for the API smoke collection.',
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        },
    )
    if created:
        Question.objects.create(
            quiz=quiz,
            question_title='Which HTTP status signals a successful deletion?',
            question_options=['204', '301', '404', '500'],
            answer='204',
        )


if __name__ == '__main__':
    main()
