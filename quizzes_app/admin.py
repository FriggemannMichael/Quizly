from django.contrib import admin

from quizzes_app.models import Question, Quiz


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin review view for generated quizzes."""

    list_display = ('title', 'owner', 'video_url', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'video_url')
    list_filter = ('created_at', 'updated_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin review view for generated questions."""

    list_display = ('question_title', 'quiz', 'answer', 'created_at', 'updated_at')
    search_fields = ('question_title', 'answer', 'quiz__title')
    list_filter = ('created_at', 'updated_at')
