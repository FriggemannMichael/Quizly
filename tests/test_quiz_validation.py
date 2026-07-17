import copy

import pytest
from django.contrib.auth import get_user_model

from quizzes_app.models import Question, Quiz
from quizzes_app.validation import (
    EXPECTED_OPTION_COUNT,
    EXPECTED_QUESTION_COUNT,
    QuizValidationError,
    validate_quiz_payload,
)


def _question(index):
    """Return a structurally valid question."""
    return {
        'question_title': f'Question {index}?',
        'question_options': [f'Option {index}{letter}' for letter in 'ABCD'],
        'answer': f'Option {index}A',
    }


def _payload(**overrides):
    """Return a structurally valid quiz payload with optional overrides."""
    payload = {
        'title': 'Django Basics',
        'description': 'A short intro to Django.',
        'questions': [_question(i) for i in range(EXPECTED_QUESTION_COUNT)],
    }
    payload.update(overrides)
    return payload


def test_valid_payload_is_returned_unchanged():
    payload = _payload()

    assert validate_quiz_payload(copy.deepcopy(payload)) == payload


def test_payload_must_be_a_dict():
    with pytest.raises(QuizValidationError):
        validate_quiz_payload(['not', 'a', 'quiz'])


@pytest.mark.parametrize('field', ['title', 'description'])
def test_required_text_field_must_be_present(field):
    payload = _payload()
    del payload[field]

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


@pytest.mark.parametrize('field', ['title', 'description'])
@pytest.mark.parametrize('value', ['', '   ', None, 42])
def test_required_text_field_must_be_a_non_empty_string(field, value):
    with pytest.raises(QuizValidationError):
        validate_quiz_payload(_payload(**{field: value}))


def test_questions_must_be_a_list():
    with pytest.raises(QuizValidationError):
        validate_quiz_payload(_payload(questions='ten questions'))


@pytest.mark.parametrize('count', [0, 9, 11])
def test_questions_must_number_exactly_ten(count):
    with pytest.raises(QuizValidationError):
        validate_quiz_payload(_payload(questions=[_question(i) for i in range(count)]))


def test_question_must_be_a_dict():
    payload = _payload()
    payload['questions'][3] = 'not a question'

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


@pytest.mark.parametrize('value', ['', '   ', None, 7])
def test_question_title_must_be_a_non_empty_string(value):
    payload = _payload()
    payload['questions'][0]['question_title'] = value

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


def test_question_title_must_be_present():
    payload = _payload()
    del payload['questions'][0]['question_title']

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


@pytest.mark.parametrize('count', [3, 5])
def test_question_must_have_exactly_four_options(count):
    payload = _payload()
    payload['questions'][2]['question_options'] = [f'Option {i}' for i in range(count)]
    payload['questions'][2]['answer'] = 'Option 0'

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


def test_question_options_must_be_a_list():
    payload = _payload()
    payload['questions'][0]['question_options'] = 'A, B, C, D'

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


@pytest.mark.parametrize('bad', ['', '   ', None, 5])
def test_question_options_must_all_be_non_empty_strings(bad):
    payload = _payload()
    payload['questions'][0]['question_options'][2] = bad

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


def test_question_options_must_be_distinct():
    payload = _payload()
    payload['questions'][0]['question_options'] = ['A', 'B', 'B', 'D']
    payload['questions'][0]['answer'] = 'A'

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


def test_answer_must_be_one_of_the_options():
    payload = _payload()
    payload['questions'][5]['answer'] = 'Something else entirely'

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


def test_answer_must_be_present():
    payload = _payload()
    del payload['questions'][5]['answer']

    with pytest.raises(QuizValidationError):
        validate_quiz_payload(payload)


def test_error_names_the_offending_question():
    payload = _payload()
    payload['questions'][7]['answer'] = 'Not an option'

    with pytest.raises(QuizValidationError, match='8'):
        validate_quiz_payload(payload)


def test_expected_counts_match_the_documented_prompt():
    assert EXPECTED_QUESTION_COUNT == 10
    assert EXPECTED_OPTION_COUNT == 4


@pytest.mark.django_db
def test_validated_payload_can_be_saved_through_the_models():
    """A payload that passes validation must survive the models' own checks."""
    payload = validate_quiz_payload(_payload())
    user = get_user_model().objects.create_user(username='mentor')

    quiz = Quiz(
        owner=user,
        title=payload['title'],
        description=payload['description'],
        video_url='https://www.youtube.com/watch?v=abc123',
    )
    quiz.full_clean()
    quiz.save()
    for data in payload['questions']:
        question = Question(quiz=quiz, **data)
        question.full_clean()
        question.save()

    assert quiz.questions.count() == EXPECTED_QUESTION_COUNT
