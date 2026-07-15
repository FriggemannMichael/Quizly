from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def validate_question_options(options: object) -> None:
    """Ensure question options are a list of exactly four non-empty strings."""
    if not isinstance(options, list):
        raise ValidationError('Question options must be a list.')
    if len(options) != 4:
        raise ValidationError('Question options must contain exactly four items.')
    if not all(isinstance(option, str) and option for option in options):
        raise ValidationError('Question options must contain four non-empty strings.')


class Quiz(models.Model):
    """Generated quiz owned by a user."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quizzes',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    """Generated question attached to a quiz."""

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_title = models.CharField(max_length=500)
    question_options = models.JSONField(validators=[validate_question_options])
    answer = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.question_title

    def clean(self) -> None:
        """Validate that the stored answer matches one of the options."""
        super().clean()
        if self.answer not in self.question_options:
            raise ValidationError({'answer': 'Answer must be one of the options.'})
