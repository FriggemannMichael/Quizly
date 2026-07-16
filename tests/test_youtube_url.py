import pytest
from rest_framework.exceptions import ValidationError

from quizzes_app.utils import normalize_youtube_url

VIDEO_ID = 'dQw4w9WgXcQ'
CANONICAL = f'https://www.youtube.com/watch?v={VIDEO_ID}'


@pytest.mark.parametrize(
    'url',
    [
        f'https://www.youtube.com/watch?v={VIDEO_ID}',
        f'http://www.youtube.com/watch?v={VIDEO_ID}',
        f'https://youtube.com/watch?v={VIDEO_ID}',
        f'https://m.youtube.com/watch?v={VIDEO_ID}',
        f'https://youtu.be/{VIDEO_ID}',
        f'https://www.youtube.com/shorts/{VIDEO_ID}',
        f'https://www.youtube.com/embed/{VIDEO_ID}',
        f'https://www.youtube.com/watch?v={VIDEO_ID}&t=42s',
        f'https://youtu.be/{VIDEO_ID}?t=42',
        f'  https://youtu.be/{VIDEO_ID}  ',
    ],
)
def test_normalize_returns_canonical_watch_url(url):
    assert normalize_youtube_url(url) == CANONICAL


@pytest.mark.parametrize(
    'url',
    [
        'https://vimeo.com/123456789',
        'https://www.google.com/watch?v=dQw4w9WgXcQ',
        'https://www.youtube.com/watch',
        'https://www.youtube.com/watch?v=',
        'https://www.youtube.com/watch?v=tooShort',
        'not-a-url',
        '',
    ],
)
def test_normalize_rejects_invalid_urls(url):
    with pytest.raises(ValidationError):
        normalize_youtube_url(url)


@pytest.mark.parametrize(
    'url',
    [
        'https://www.youtube.com/playlist?list=PLtQ8bWL8dN00abcdEFGH',
        f'https://www.youtube.com/watch?v={VIDEO_ID}&list=PLtQ8bWL8dN00abcdEFGH',
    ],
)
def test_normalize_rejects_playlist_urls(url):
    with pytest.raises(ValidationError):
        normalize_youtube_url(url)
