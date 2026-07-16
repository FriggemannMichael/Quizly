from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from yt_dlp.utils import DownloadError

from quizzes_app.audio import AudioExtractionError, extract_audio

VIDEO_URL = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
VIDEO_ID = 'dQw4w9WgXcQ'
YDL_TARGET = 'quizzes_app.audio.yt_dlp.YoutubeDL'


def _fake_ydl(opts):
    """Fake YoutubeDL that writes a dummy mp3 next to the configured outtmpl."""
    ydl = MagicMock()
    ydl.__exit__.return_value = False

    def extract_info(url, download):
        (Path(opts['outtmpl']).parent / f'{VIDEO_ID}.mp3').write_bytes(b'audio')
        return {'id': VIDEO_ID}

    ydl.__enter__.return_value.extract_info.side_effect = extract_info
    return ydl


def test_extract_audio_uses_required_ydl_opts():
    captured = {}

    def make_ydl(opts):
        captured['opts'] = opts
        return _fake_ydl(opts)

    with patch(YDL_TARGET, side_effect=make_ydl):
        with extract_audio(VIDEO_URL):
            pass

    assert captured['opts']['format'] == 'bestaudio/best'
    assert captured['opts']['quiet'] is True
    assert captured['opts']['noplaylist'] is True


def test_extract_audio_yields_path_and_cleans_up():
    with patch(YDL_TARGET, side_effect=_fake_ydl):
        with extract_audio(VIDEO_URL) as audio_path:
            assert audio_path.name == f'{VIDEO_ID}.mp3'
            assert audio_path.exists()
            saved = audio_path

    assert not saved.exists()


def test_extract_audio_requests_download_for_url():
    captured = {}

    def make_ydl(opts):
        ydl = MagicMock()
        ydl.__exit__.return_value = False

        def extract_info(url, download):
            captured['url'] = url
            captured['download'] = download
            (Path(opts['outtmpl']).parent / f'{VIDEO_ID}.mp3').write_bytes(b'a')
            return {'id': VIDEO_ID}

        ydl.__enter__.return_value.extract_info.side_effect = extract_info
        return ydl

    with patch(YDL_TARGET, side_effect=make_ydl):
        with extract_audio(VIDEO_URL):
            pass

    assert captured['url'] == VIDEO_URL
    assert captured['download'] is True


def test_extract_audio_wraps_download_errors():
    def failing(opts):
        ydl = MagicMock()
        ydl.__exit__.return_value = False
        ydl.__enter__.return_value.extract_info.side_effect = DownloadError('boom')
        return ydl

    with patch(YDL_TARGET, side_effect=failing):
        with pytest.raises(AudioExtractionError):
            with extract_audio(VIDEO_URL):
                pass
