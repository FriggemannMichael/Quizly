# Quizly Backend

**Quizly** turns a YouTube video into a playable quiz. The backend downloads the
video's audio with *yt-dlp*, transcribes it locally with *Whisper*, and lets
*Gemini Flash* generate ten multiple-choice questions with four options each.
Users register, log in with JWT cookies, and manage their own quizzes through a
REST API consumed by the provided static frontend.

## Setup

FFmpeg must be installed globally first — both the audio extraction
(`quizzes_app/audio.py`) and the Whisper transcription
(`quizzes_app/transcription.py`) shell out to it, so quiz generation fails
without it.

Windows (PowerShell):

```powershell
winget install --id Gyan.FFmpeg -e --source winget
# or manually: download from https://ffmpeg.org/download.html, unpack to
# C:\ffmpeg, and add C:\ffmpeg\bin to the Path environment variable.

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

macOS / Linux:

```bash
brew install ffmpeg          # or: sudo apt install ffmpeg

python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Verify FFmpeg in a **new** terminal (so a changed `Path` is picked up) — this
must print a version:

```powershell
ffmpeg -version
```

Then open `.env` and fill in `GEMINI_API_KEY` (see below). The other values
work as they are for local development. The API is served at
`http://127.0.0.1:8000/api/`.

## Features

- **User accounts** - registration, login, and logout backed by Django's user
  model with validated passwords.
- **Cookie-based JWT auth** - access and refresh tokens are delivered as
  HttpOnly cookies; a token refresh endpoint rotates the access token and a
  blacklist invalidates refresh tokens on logout.
- **Quiz generation** - `POST /api/quizzes/` runs the yt-dlp → Whisper →
  Gemini pipeline and stores a quiz with exactly ten questions and four
  options each; transient Gemini errors are retried with backoff.
- **Quiz management** - owner-scoped list, detail, partial update (title and
  description), and delete endpoints; nobody can read or touch another user's
  quizzes.
- **Canonical video URLs** - every accepted YouTube URL is normalized to
  `https://www.youtube.com/watch?v=<id>` so the frontend can embed it.
- **Admin curation** - quizzes and questions are editable in the Django admin;
  creating and deleting stays with the pipeline and the API.

## Tech stack

- Python 3.13
- Django 5.2 with Django REST Framework
- Simple JWT with HttpOnly cookie delivery and token blacklist
- yt-dlp and FFmpeg for audio extraction
- OpenAI Whisper (local) for transcription
- Google Gemini Flash (`gemini-3.5-flash`) for quiz generation
- SQLite for local development
- pytest with coverage gate, ruff, GitHub Actions CI

## Authentication

The provided frontend never sends an `Authorization` header. It relies on two
HttpOnly cookies, `access_token` and `refresh_token`, which the backend sets on
login and clears on logout:

- `POST /api/register/` - create an account.
- `POST /api/login/` - validate credentials, set both cookies, return the user.
- `POST /api/token/refresh/` - read the refresh cookie (no body), set a fresh
  access cookie.
- `POST /api/logout/` - blacklist the refresh token and delete both cookies.

Protected endpoints authenticate from the access cookie
(`accounts/authentication.py`). Credentialed CORS is preconfigured for the
local frontend origins `http://127.0.0.1:5500` and `http://localhost:5500`.

## Environment variables

`config/settings.py` loads `.env` from the project root at startup. Real
environment variables take precedence over the file, which keeps CI and
production authoritative. A missing `.env` is ignored and every variable falls
back to its default. `.env` is git-ignored and must never be committed.

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

Treat it like a password: it is tied to your Google account and its quota.
Never commit it, never paste it into a chat or an issue. If it leaks, delete
the key in AI Studio and create a new one — that is the only real fix.

The model is pinned in `quizzes_app/generation.py` as `gemini-3.5-flash`.
Older models are not usable with a newly created key: `gemini-2.0-flash`
reports a free-tier quota of `limit: 0`, and `gemini-2.5-flash` answers
`404 — no longer available to new users`. If generation suddenly fails with
`404` or `429`, check the available models before suspecting the code:

```powershell
python -c "from dotenv import load_dotenv; load_dotenv(); from google import genai; import os; c = genai.Client(api_key=os.environ['GEMINI_API_KEY']); [print(m.name) for m in c.models.list()]"
```

Note that listing a model is not the same as being allowed to call it: the
retired models above still appear in this list.

## Project structure

- `accounts/` - registration, login, logout, and the cookie JWT
  authentication class.
- `quizzes_app/` - quiz models, serializers, permissions, the REST views, and
  the generation pipeline (audio, transcription, Gemini, validation).
- `core/` - shared cookie helpers.
- `config/` - settings, URL routing, and `.env` loading.
- `tests/` - pytest suite, Postman smoke collection, and the size-limit
  script.
- `docs/` - API contract, frontend integration notes, and acceptance
  checklists.

## Running checks

These are the same checks CI runs, in the same order. Run them before pushing:

```powershell
ruff check .
ruff format --check .
python manage.py check
pytest
python tests/scripts/check_size_limits.py
```

`ruff format --check .` only reports; use `ruff format .` to actually apply
the formatting.

CI (GitHub Actions) additionally runs migrations and the Postman auth smoke
collection against a live server. To run it locally after starting
`python manage.py runserver`:

```powershell
npx --yes newman@6.2.1 run tests/postman/quizly-auth.postman_collection.json --env-var baseUrl=http://127.0.0.1:8000
```

## Delivery checklist

See [docs/acceptance-checklist.md](docs/acceptance-checklist.md) for every
mentor requirement mapped to its implementation and tests. Key points:

- All API endpoints from the contract are implemented and tested
  (171 tests, 100% coverage, enforced 95% floor).
- Functions stay within 14 lines, enforced by the CI size gate.
- The provided frontend runs against this backend without modification.

## Repository hygiene

Not part of version control:

- `.env` (secrets), `db.sqlite3` (local data), `.venv/` (environment)
- The provided frontend repository — it is consumed read-only and lives
  outside this project.
