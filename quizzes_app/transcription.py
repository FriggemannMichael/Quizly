from pathlib import Path

import whisper

DEFAULT_MODEL_NAME = 'base'


class TranscriptionError(Exception):
    """Raised when Whisper cannot transcribe an audio file."""


def transcribe_audio(audio_path: Path, model_name: str = DEFAULT_MODEL_NAME) -> str:
    """Return the plain transcript text for an audio file.

    Loading a Whisper model pulls in torch and downloads model weights on
    first use, so callers should treat this as a heavy operation.
    """
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(str(audio_path))
    except (RuntimeError, OSError) as error:
        raise TranscriptionError(str(error)) from error
    return result['text'].strip()
