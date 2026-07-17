from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quizzes_app.audio import AudioExtractionError
from quizzes_app.generation import QuizGenerationError
from quizzes_app.pipeline import generate_quiz_payload, save_quiz
from quizzes_app.serializers import QuizCreateSerializer, QuizSerializer
from quizzes_app.transcription import TranscriptionError
from quizzes_app.validation import QuizValidationError

PIPELINE_ERRORS = (
    AudioExtractionError,
    TranscriptionError,
    QuizGenerationError,
    QuizValidationError,
)


class QuizGenerationFailed(APIException):
    """Report that the generation pipeline could not produce a usable quiz."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Quiz generation failed.'


class QuizListCreateView(APIView):
    """Create quizzes from submitted YouTube URLs."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_url = serializer.validated_data['url']
        payload = _generated_payload(video_url)
        quiz = save_quiz(request.user, video_url, payload)
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


def _generated_payload(video_url: str) -> dict:
    """Run the pipeline, turning external failures into a controlled error."""
    try:
        return generate_quiz_payload(video_url)
    except PIPELINE_ERRORS as error:
        raise QuizGenerationFailed() from error
