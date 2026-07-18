from django.contrib import admin
from django.http import HttpRequest

from quizzes_app.models import Question, Quiz


class GeneratedContentAdmin(admin.ModelAdmin):
    """Base admin for generated records: editable, but not added or deleted.

    Quizzes and questions are created by the generation pipeline and removed
    through the API, so the admin only curates existing records.
    """

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Disallow creating records through the admin."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        """Disallow deleting records through the admin."""
        return False


@admin.register(Quiz)
class QuizAdmin(GeneratedContentAdmin):
    """Admin curation view for generated quizzes."""

    list_display = ('title', 'owner', 'video_url', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'video_url')
    list_filter = ('created_at', 'updated_at')


@admin.register(Question)
class QuestionAdmin(GeneratedContentAdmin):
    """Admin curation view for generated questions."""

    list_display = ('question_title', 'quiz', 'answer', 'created_at', 'updated_at')
    search_fields = ('question_title', 'answer', 'quiz__title')
    list_filter = ('created_at', 'updated_at')
