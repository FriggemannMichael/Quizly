# Dependency Decisions

This document tracks dependency decisions derived from the project docs and frontend analysis.

## Installed Now

### `django-cors-headers==4.9.0`

Reason: The provided frontend is served separately and sends authenticated requests with `credentials: "include"`. The backend must support credentialed CORS.

Configuration added:

- `corsheaders` in `INSTALLED_APPS`
- `corsheaders.middleware.CorsMiddleware` first in `MIDDLEWARE`
- `CORS_ALLOWED_ORIGINS`
- `CORS_ALLOW_CREDENTIALS = True`
- `CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS`

### `yt-dlp==2025.7.21`

Reason: The mentor checklist explicitly references the 2025.07.21 yt-dlp version for downloading YouTube audio.

Required options from project notes:

```python
ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": tmp_filename,
    "quiet": True,
    "noplaylist": True,
}
```

### `google-genai==2.11.0`

Reason: The project must use Gemini Flash for quiz generation.

Runtime configuration needed later:

```text
GEMINI_API_KEY=<key>
```

### `python-dotenv==1.2.2`

Reason: `.env.example` documents a `.env` workflow, but nothing read the file, so every setting silently fell back to its default unless the variable was exported by hand or by an IDE run configuration.

`config/env.py::load_env_file` is called from `config/settings.py` before the first `os.environ.get`. It uses `override=False`, so a real environment variable always wins over `.env` and CI and production stay authoritative. A missing `.env` is ignored.

Chosen over `django-environ` because the project already reads plain `os.environ` values and only needs the file loaded, not a second settings-parsing API.

### Simple JWT blacklist app

Reason: Logout must invalidate refresh tokens.

No new package was needed because blacklist support is included in `djangorestframework_simplejwt`. The app `rest_framework_simplejwt.token_blacklist` is enabled and migrations were run locally.

## Deferred

### `openai-whisper==20250625`

Reason: Whisper is required for the transcription workflow, but it pulls in heavy packages such as `torch`, `numba`, `numpy`, and `tiktoken`. It should be added when the transcription service is implemented, so CI and local setup do not become heavy before the code uses it.

Dry-run dependency set observed:

- `torch==2.13.0`
- `numba==0.66.0`
- `numpy==2.4.6`
- `tiktoken==0.13.0`
- `llvmlite==0.48.0`
- `tqdm==4.68.4`
- plus supporting packages

## External System Requirement

### FFmpeg

FFmpeg is not a Python package and must be installed globally. It is required by the future audio/transcription workflow.
