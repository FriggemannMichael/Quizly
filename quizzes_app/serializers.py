from rest_framework import serializers

from quizzes_app.models import Question, Quiz
from quizzes_app.utils import normalize_youtube_url


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize a generated question for quiz responses."""

    class Meta:
        model = Question
        fields = [
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at',
        ]


class QuizSerializer(serializers.ModelSerializer):
    """Serialize a quiz together with all of its questions."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions',
        ]


class QuizUpdateSerializer(serializers.ModelSerializer):
    """Validate partial quiz updates limited to the editable fields."""

    class Meta:
        model = Quiz
        fields = ['title', 'description']


class QuizCreateSerializer(serializers.Serializer):
    """Validate quiz creation requests and normalize the submitted video URL."""

    url = serializers.CharField()

    def validate_url(self, value: str) -> str:
        """Return the canonical watch URL for the submitted video."""
        return normalize_youtube_url(value)
