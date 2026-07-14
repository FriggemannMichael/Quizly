import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from quizzes_app.models import Question, Quiz

pytestmark = pytest.mark.django_db


def test_quiz_belongs_to_user():
    user = get_user_model().objects.create_user(username='mentor')

    quiz = Quiz.objects.create(
        owner=user,
        title='Django Basics',
        description='A short Django quiz',
        video_url='https://www.youtube.com/watch?v=abc123',
    )

    assert quiz.owner == user
    assert list(user.quizzes.all()) == [quiz]


def test_question_options_must_be_four_strings():
    user = get_user_model().objects.create_user(username='mentor')
    quiz = Quiz.objects.create(owner=user, title='Quiz', video_url='https://x.test')
    question = Question(
        quiz=quiz,
        question_title='What is Django?',
        question_options=['Framework', 'Database', 'Browser'],
        answer='Framework',
    )

    with pytest.raises(ValidationError):
        question.full_clean()


def test_question_answer_must_be_in_options():
    user = get_user_model().objects.create_user(username='mentor')
    quiz = Quiz.objects.create(owner=user, title='Quiz', video_url='https://x.test')
    question = Question(
        quiz=quiz,
        question_title='What is Django?',
        question_options=['Framework', 'Database', 'Browser', 'Editor'],
        answer='Language',
    )

    with pytest.raises(ValidationError):
        question.full_clean()


def test_deleting_quiz_deletes_questions():
    user = get_user_model().objects.create_user(username='mentor')
    quiz = Quiz.objects.create(owner=user, title='Quiz', video_url='https://x.test')
    Question.objects.create(
        quiz=quiz,
        question_title='What is Django?',
        question_options=['Framework', 'Database', 'Browser', 'Editor'],
        answer='Framework',
    )

    quiz.delete()

    assert Question.objects.count() == 0


def test_question_options_must_be_a_list_of_strings():
    user = get_user_model().objects.create_user(username='mentor2')
    quiz = Quiz.objects.create(owner=user, title='Quiz', video_url='https://x.test')
    question = Question(
        quiz=quiz,
        question_title='What is Django?',
        question_options=['Framework', 'Database', 'Browser', 42],
        answer='Framework',
    )

    with pytest.raises(ValidationError):
        question.full_clean()


def test_model_string_representations_are_readable():
    user = get_user_model().objects.create_user(username='mentor3')
    quiz = Quiz.objects.create(owner=user, title='Quiz', video_url='https://x.test')
    question = Question.objects.create(
        quiz=quiz,
        question_title='What is Django?',
        question_options=['Framework', 'Database', 'Browser', 'Editor'],
        answer='Framework',
    )

    assert str(quiz) == 'Quiz'
    assert str(question) == 'What is Django?'


def test_question_options_must_be_a_json_array():
    user = get_user_model().objects.create_user(username='mentor4')
    quiz = Quiz.objects.create(owner=user, title='Quiz', video_url='https://x.test')
    question = Question(
        quiz=quiz,
        question_title='What is Django?',
        question_options='Framework,Database,Browser,Editor',
        answer='Framework',
    )

    with pytest.raises(ValidationError):
        question.full_clean()
