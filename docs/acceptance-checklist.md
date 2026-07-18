# Final Acceptance Checklist

Maps every requirement from the [mentor checklist](mentor-checkliste.md) to its
implementation status and evidence. Items owned by the provided static frontend
are marked "provided frontend" — the backend serves them but the UI behavior
ships with the frontend repository (see
[frontend integration notes](frontend-integration.md)).

Status as of 2026-07-18.

## Open Items

- [ ] **Legal pages operator data (User Story 10).** The provided frontend
  ships imprint and privacy pages; the operator's personal data must be filled
  in before going live. Frontend-side task, not tracked in this repository.

## 1. Technical Requirements

### Clean Code

- [x] Functions are at most 14 lines — enforced in CI by
  `tests/scripts/check_size_limits.py` (`MAX_FUNCTION_LOC = 14`).
- [x] Each function has a single responsibility — kept small by the size gate;
  helpers split into `accounts/utils.py`, `quizzes_app/pipeline.py`,
  `quizzes_app/utils.py`, `core/cookies.py`.
- [x] Function names follow snake_case — enforced by `ruff check` (pep8-naming
  rules, `pyproject.toml`).
- [x] Meaningful variable names — reviewed throughout; ruff flags single-letter
  and unused names.
- [x] All declared variables and functions are used — `ruff check` (unused
  imports/variables) runs in CI.
- [x] No commented-out code — `ruff check` (eradicate rules) plus review.

### Documentation

- [x] Docstrings present — every module, class, and function in `accounts/`,
  `quizzes_app/`, `core/`, and `config/` carries one.
- [x] Meaningful `README.md` — covers setup, environment variables, FFMPEG
  requirement, code quality commands, and Postman smoke tests.

### Django-Specific

- [x] Code lives in the right file — `accounts/views.py` and
  `quizzes_app/views.py` contain only views returning responses; helpers live
  in `accounts/utils.py`, `quizzes_app/pipeline.py`, `quizzes_app/utils.py`,
  and `quizzes_app/validation.py`.
- [x] Admin panel allows editing quizzes and questions —
  `quizzes_app/admin.py` (`GeneratedContentAdmin`: change permission enabled,
  add/delete stay blocked because records are created by the pipeline and
  removed through the API); tests: `tests/test_quiz_admin.py`.

### Pythonic Style

- [x] PEP-8 compliant — `ruff check .` and `ruff format --check .` gate every
  push (`.github/workflows/ci.yml`, required status check `checks`).

### Other Technical Requirements

- [x] Backend and frontend are separated and speak REST — frontend is a
  separate repository consumed read-only; contract verified with zero
  mismatches (`frontend-integration.md`, PR #56).
- [x] JWT authentication via HTTP-only cookies — `core/cookies.py`,
  `accounts/authentication.py` (`CookieJWTAuthentication` is the DRF default);
  tests: `tests/test_cookie_authentication.py`, `tests/test_core_cookies.py`.
- [x] FFMPEG globally installed and documented in the README — README
  "Prerequisites" section includes install and verify steps.
- [x] YouTube-only audio extraction with yt_dlp — `quizzes_app/audio.py`;
  URL validation/normalization in `quizzes_app/utils.py`; tests:
  `tests/test_audio_extraction.py`, `tests/test_youtube_url.py`.
- [x] Transcription with Whisper (local) — `quizzes_app/transcription.py`;
  tests: `tests/test_transcription.py`.
- [x] Quiz generation with Gemini Flash — `quizzes_app/generation.py`
  (`gemini-3.5-flash`, with transient-error retry); tests:
  `tests/test_quiz_generation.py`.

## 2. User Account & Registration

### User Story 1: Registration

- [x] Registration endpoint validates and stores the user —
  `POST /api/register/` (`accounts/views.py::RegisterView`,
  `accounts/serializers.py::RegisterSerializer`); tests:
  `tests/test_registration_api.py`. Form UI: provided frontend.
- [x] Invalid input returns an error message the frontend displays —
  validation details include duplicate username/email cases.
- [x] Switch to login form — provided frontend.

### User Story 2: Login

- [x] Login endpoint with username and password —
  `POST /api/login/` (`accounts/views.py::LoginView`); tests:
  `tests/test_login_api.py`. Form UI: provided frontend.
- [x] Wrong credentials return an error, kept generic for security —
  `accounts/utils.py::validated_login_serializer` always answers
  "Invalid credentials."
- [x] JWT access + refresh tokens delivered as HTTP-only cookies —
  `core/cookies.py` (`access_token`, `refresh_token`, HttpOnly, SameSite=Lax);
  cookie-based authentication for all protected endpoints.
- [x] Redirect to start page after login / switch to registration — provided
  frontend.

### User Story 3: Logout

- [x] Logout endpoint identified via cookie tokens, cookies cleared —
  `POST /api/logout/` (`accounts/views.py::LogoutView`); tests:
  `tests/test_logout_api.py`. UI option and redirect: provided frontend.
- [x] Used refresh tokens become unusable after logout — Simple JWT token
  blacklist (`rest_framework_simplejwt.token_blacklist` in
  `config/settings.py`); blacklisting covered in `tests/test_logout_api.py`.

## 3. Quiz

### User Story 4: Generate a new quiz

- [x] URL in, quiz out: yt_dlp + FFMPEG audio extraction, Whisper
  transcription, Gemini prompt, storage — pipeline wired in
  `quizzes_app/pipeline.py` behind `POST /api/quizzes/`; tests:
  `tests/test_quiz_api.py`. Dashboard input field: provided frontend.
- [x] 10 questions with 4 options each — enforced by the prompt
  (`quizzes_app/prompts.py`) and validated in `quizzes_app/validation.py`;
  tests: `tests/test_quiz_validation.py`, `tests/test_quiz_models.py`.

### User Story 5: Replay existing quizzes

- [x] Overview of the user's quizzes — `GET /api/quizzes/` returns the
  owner-filtered list with all questions; tests: `tests/test_quiz_list_api.py`.
  Overview UI: provided frontend.

### User Story 6: Quiz detail view

- [x] Title and description editable, persisted in the backend —
  `PATCH /api/quizzes/{id}/` restricted to those two fields; tests:
  `tests/test_quiz_update_api.py`.
- [x] Embedded YouTube video — `video_url` stored in canonical
  `watch?v=<id>` form (`quizzes_app/utils.py::normalize_youtube_url`) so the
  frontend can derive the embed URL; tests: `tests/test_youtube_url.py`.
- [x] Quiz start buttons — provided frontend.

### User Story 7: Sidebar (today / last 7 days / all)

- [x] Backend supplies `created_at`/`updated_at` as ISO timestamps on
  `GET /api/quizzes/` and `GET /api/quizzes/{id}/` for the frontend's date
  filtering; deletion via `DELETE /api/quizzes/{id}/`; tests:
  `tests/test_quiz_detail_api.py`, `tests/test_quiz_delete_api.py`. Sidebar
  UI and date grouping: provided frontend.

### User Story 8: Playing a quiz

- [x] Progress saving and answer revision during play — provided frontend
  (client-side state); the backend serves the full question set including
  `answer` for evaluation.

### User Story 9: Quiz evaluation

- [x] Score, answer review, and navigation back to the overview — provided
  frontend; computed client-side from the delivered `questions` array.

### User Story 10: Legal information

- [x] Imprint and privacy pages with footer links, structured and responsive —
  provided frontend.
- [ ] Operator data must be completed before going live — **open**, see Open
  Items above.
