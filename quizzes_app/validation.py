EXPECTED_QUESTION_COUNT = 10
EXPECTED_OPTION_COUNT = 4


class QuizValidationError(Exception):
    """Raised when generated quiz data does not match the required structure."""


def validate_quiz_payload(payload: object) -> dict:
    """Return generated quiz data unchanged once it matches the required structure.

    Gemini is instructed to produce this shape but is not bound to it, so the
    data is checked before anything is saved.
    """
    if not isinstance(payload, dict):
        raise QuizValidationError('Quiz must be a JSON object.')
    _require_text(payload, 'title', 'Quiz')
    _require_text(payload, 'description', 'Quiz')
    _validate_questions(payload.get('questions'))
    return payload


def _validate_questions(questions: object) -> None:
    """Check that the quiz carries exactly the expected number of questions."""
    if not isinstance(questions, list):
        raise QuizValidationError('Quiz questions must be a list.')
    if len(questions) != EXPECTED_QUESTION_COUNT:
        raise QuizValidationError(
            f'Quiz must contain exactly {EXPECTED_QUESTION_COUNT} questions, '
            f'got {len(questions)}.'
        )
    for number, question in enumerate(questions, start=1):
        _validate_question(question, number)


def _validate_question(question: object, number: int) -> None:
    """Check a single question, naming its position in any error."""
    label = f'Question {number}'
    if not isinstance(question, dict):
        raise QuizValidationError(f'{label} must be a JSON object.')
    _require_text(question, 'question_title', label)
    options = _validate_options(question.get('question_options'), label)
    _require_text(question, 'answer', label)
    if question['answer'] not in options:
        raise QuizValidationError(f'{label} answer must be one of its options.')


def _validate_options(options: object, label: str) -> list:
    """Check that a question offers exactly four distinct, non-empty options."""
    if not isinstance(options, list):
        raise QuizValidationError(f'{label} options must be a list.')
    if len(options) != EXPECTED_OPTION_COUNT:
        raise QuizValidationError(
            f'{label} must have exactly {EXPECTED_OPTION_COUNT} options, '
            f'got {len(options)}.'
        )
    if not all(_is_text(option) for option in options):
        raise QuizValidationError(f'{label} options must be non-empty strings.')
    if len(set(options)) != EXPECTED_OPTION_COUNT:
        raise QuizValidationError(f'{label} options must be distinct.')
    return options


def _require_text(data: dict, field: str, label: str) -> None:
    """Check that a field holds a non-empty string."""
    if not _is_text(data.get(field)):
        raise QuizValidationError(f'{label} {field} must be a non-empty string.')


def _is_text(value: object) -> bool:
    """Return whether a value is a string with visible characters."""
    return isinstance(value, str) and bool(value.strip())
