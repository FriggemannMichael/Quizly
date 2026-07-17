# Quizly

Generates a quiz from a YouTube video: the audio is downloaded with yt-dlp, transcribed with Whisper, and turned into questions by Gemini.

## Requirements

- Python 3.13
- FFmpeg, installed globally (see below)

## FFmpeg

FFmpeg is not a Python package and must be installed on the system. Both the audio
extraction (`quizzes_app/audio.py`) and the Whisper transcription
(`quizzes_app/transcription.py`) shell out to it, so quiz generation fails without it.

Windows, via winget:

```powershell
winget install --id Gyan.FFmpeg -e --source winget
```

Windows, manually: download a build from <https://ffmpeg.org/download.html>, unpack it
to for example `C:\ffmpeg`, and add `C:\ffmpeg\bin` to the `Path` environment variable.

macOS:

```bash
brew install ffmpeg
```

Verify the installation — this must print a version, in a **new** terminal so that a
changed `Path` is picked up:

```powershell
ffmpeg -version
```

## Local setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

Then open `.env` and fill in `GEMINI_API_KEY`. The other values work as they are for
local development.

## Environment variables

`config/settings.py` loads `.env` from the project root at startup, so no shell export
is needed. Real environment variables take precedence over the file, which keeps CI and
production authoritative. A missing `.env` is ignored and every variable falls back to
its default.

`.env` is git-ignored and must never be committed.

| Variable | Purpose | Default |
| --- | --- | --- |
| `GEMINI_API_KEY` | Quiz generation. Without it, `POST` quiz creation fails; the rest of the app runs. | none |
| `DJANGO_SECRET_KEY` | Django signing key. Use a real, random value in production. | insecure dev key |
| `DJANGO_DEBUG` | `true` or `false`. | `true` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host list. | empty |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Comma-separated origins allowed to send credentialed requests. | `http://127.0.0.1:5500,http://localhost:5500` |

### GEMINI_API_KEY

Create a key at <https://aistudio.google.com/apikey> and put it in `.env`:

```text
GEMINI_API_KEY=your-key
```

Treat it like a password: it is tied to your Google account and its quota. Never commit
it, never paste it into a chat or an issue. If it leaks, delete the key in AI Studio and
create a new one — that is the only real fix.

The model is pinned in `quizzes_app/generation.py` as `gemini-3.5-flash`. Older models
are not usable with a newly created key: `gemini-2.0-flash` reports a free-tier quota of
`limit: 0`, and `gemini-2.5-flash` answers `404 — no longer available to new users`. If
generation suddenly fails with `404` or `429`, check the available models before
suspecting the code:

```powershell
python -c "from dotenv import load_dotenv; load_dotenv(); from google import genai; import os; c = genai.Client(api_key=os.environ['GEMINI_API_KEY']); [print(m.name) for m in c.models.list()]"
```

Note that listing a model is not the same as being allowed to call it: the retired
models above still appear in this list.

## Code quality

These are the same checks CI runs, in the same order. Run them before pushing:

```powershell
ruff check .
ruff format --check .
python manage.py check
pytest
python tests/scripts/check_size_limits.py
```

`ruff format --check .` only reports; use `ruff format .` to actually apply the
formatting.

## Postman smoke tests

CI runs the Postman auth smoke collection with Newman against a local Django server.
To run it locally after starting `python manage.py runserver`:

```powershell
npx --yes newman@6.2.1 run tests/postman/quizly-auth.postman_collection.json --env-var baseUrl=http://127.0.0.1:8000
```

## CI

GitHub Actions runs the same checks on pushes and pull requests to `main`.

## Django

The project uses Django 5.2 with the settings module `config.settings`.
Local SQLite data is stored in `db.sqlite3` and ignored by Git.
