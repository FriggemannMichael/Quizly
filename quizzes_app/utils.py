import re
from urllib.parse import parse_qs, urlparse

from rest_framework.exceptions import ValidationError

YOUTUBE_HOSTS = frozenset(
    {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be'}
)
PATH_ID_PREFIXES = ('/shorts/', '/embed/')
VIDEO_ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]{11}$')


def normalize_youtube_url(url: str) -> str:
    """Return the canonical watch URL for a supported YouTube video."""
    video_id = _extract_video_id(url)
    return f'https://www.youtube.com/watch?v={video_id}'


def _extract_video_id(url: str) -> str:
    """Parse a supported YouTube URL and return its validated video id."""
    parsed = urlparse(url.strip())
    if (parsed.hostname or '') not in YOUTUBE_HOSTS:
        raise ValidationError('A valid YouTube URL is required.')
    _reject_playlists(parsed)
    return _validated_id(_raw_video_id(parsed))


def _reject_playlists(parsed) -> None:
    """Reject playlist URLs, which cannot be turned into a single quiz."""
    if 'list' in parse_qs(parsed.query) or parsed.path == '/playlist':
        raise ValidationError('Playlist URLs are not supported.')


def _raw_video_id(parsed) -> str:
    """Pull the raw video id string out of the URL path or query."""
    if parsed.hostname == 'youtu.be':
        return parsed.path.lstrip('/')
    for prefix in PATH_ID_PREFIXES:
        if parsed.path.startswith(prefix):
            return parsed.path[len(prefix) :].split('/')[0]
    return parse_qs(parsed.query).get('v', [''])[0]


def _validated_id(video_id: str) -> str:
    """Return the video id if it matches the YouTube id format."""
    if not VIDEO_ID_PATTERN.match(video_id):
        raise ValidationError('A valid YouTube URL is required.')
    return video_id
