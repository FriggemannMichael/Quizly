import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError


class AudioExtractionError(Exception):
    """Raised when yt-dlp cannot extract audio from a video."""


@contextmanager
def extract_audio(video_url: str) -> Iterator[Path]:
    """Yield the extracted audio path, cleaning up the temp dir on exit."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield _download_audio(video_url, Path(tmp_dir))


def _download_audio(video_url: str, output_dir: Path) -> Path:
    """Run yt-dlp for the video and return the extracted audio path."""
    opts = _build_ydl_opts(output_dir)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
    except DownloadError as error:
        raise AudioExtractionError(str(error)) from error
    return output_dir / f'{info["id"]}.mp3'


def _build_ydl_opts(output_dir: Path) -> dict:
    """Return the yt-dlp options for audio-only extraction."""
    return {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'},
        ],
    }
