from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quizzes_app.transcription import TranscriptionError, transcribe_audio

AUDIO_PATH = Path('/tmp/audio.mp3')
LOAD_TARGET = 'quizzes_app.transcription.whisper.load_model'


def test_transcribe_returns_plain_text():
    model = MagicMock()
    model.transcribe.return_value = {'text': '  Hello world  '}

    with patch(LOAD_TARGET, return_value=model):
        text = transcribe_audio(AUDIO_PATH)

    assert text == 'Hello world'
    model.transcribe.assert_called_once_with(str(AUDIO_PATH))


def test_transcribe_uses_requested_model():
    model = MagicMock()
    model.transcribe.return_value = {'text': 'x'}

    with patch(LOAD_TARGET, return_value=model) as load_model:
        transcribe_audio(AUDIO_PATH, model_name='small')

    load_model.assert_called_once_with('small')


def test_transcribe_wraps_model_load_errors():
    with patch(LOAD_TARGET, side_effect=RuntimeError('whisper failed')):
        with pytest.raises(TranscriptionError):
            transcribe_audio(AUDIO_PATH)


def test_transcribe_wraps_missing_ffmpeg_errors():
    model = MagicMock()
    model.transcribe.side_effect = FileNotFoundError('ffmpeg not found')

    with patch(LOAD_TARGET, return_value=model):
        with pytest.raises(TranscriptionError):
            transcribe_audio(AUDIO_PATH)
