# Frontend Integration Notes

Source repository inspected temporarily at `C:\tmp\quizly-frontend`.

Frontend repository:

```text
git@github.com:Developer-Akademie-Backendkurs/project.Quizly.git
```

HTTPS clone used for inspection because SSH access was not available locally:

```text
https://github.com/Developer-Akademie-Backendkurs/project.Quizly.git
```

## Frontend Type

The frontend is a static HTML/CSS/JavaScript application. There is no package manager or build system in the inspected repository.

Important files:

- `shared/js/config.js`: API base URL and endpoint constants
- `shared/js/auth.js`: login, registration, logout, token refresh, authenticated fetch wrapper
- `shared/js/api.js`: currently empty
- `shared/js/library.js`: quiz creation and library cards
- `shared/js/quizoverview.js`: quiz detail/edit/sidebar flow
- `shared/js/quiz.js`: quiz playing, delete, results, answer review

## API Base URL

The frontend calls the backend at:

```js
const API_BASE_URL = "http://127.0.0.1:8000/api/";
```

Backend endpoints must therefore live under `/api/`.

## CORS And Cookies

All protected requests use:

```js
credentials: "include"
```

The backend must support credentialed CORS for the local frontend origin. If the frontend is served through VS Code Live Server, likely origins are:

```text
http://127.0.0.1:5500
http://localhost:5500
```

Important: for local cookie auth, prefer serving frontend and backend on the same host name, e.g. both `127.0.0.1`, because `localhost` and `127.0.0.1` may behave differently for cookies.

## Authentication Contract

The frontend does not use `Authorization` headers and does not read tokens from JSON. It expects JWTs to be stored as HttpOnly cookies.

### POST `/api/register/`

Request body created by `signUpUser`:

```json
{
  "username": "...",
  "password": "...",
  "email": "...",
  "confirmed_password": "..."
}
```

Frontend behavior:

- On success, redirects to `/pages/login.html`.
- On error, reads JSON and displays `data.username` in the toast.

Backend implication:

- Return useful validation details, especially for duplicate/invalid `username`.
- Match the documented success response if possible: `{ "detail": "User created successfully!" }`.

### POST `/api/login/`

Request body:

```json
{
  "username": "...",
  "password": "..."
}
```

Request options:

```js
credentials: "include"
```

Frontend behavior:

- It does not consume tokens from the response body.
- It expects `access_token` and `refresh_token` to be set as HttpOnly cookies.
- On success, redirects to `/pages/library.html`.
- On error, displays `responseData.detail`.

Expected response body from endpoint docs:

```json
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

Backend implication:

- Simple JWT's default `TokenObtainPairView` is not enough for `/api/login/` because it returns JSON tokens instead of setting cookies.
- Implement a custom login view that validates credentials, creates access/refresh tokens, sets HttpOnly cookies, and returns the documented body.

### POST `/api/logout/`

Request options:

```js
credentials: "include"
```

Frontend behavior:

- It does not inspect the response body deeply.
- It redirects to login after logout.

Backend implication:

- Read refresh token from cookie.
- Blacklist refresh token if Simple JWT blacklist app is enabled.
- Delete `access_token` and `refresh_token` cookies.
- Return a 200 response matching docs if possible.

### POST `/api/token/refresh/`

Request options:

```js
credentials: "include"
```

Frontend behavior:

- Sends no request body.
- Expects refresh token to come from the `refresh_token` cookie.
- If response is OK, it retries the original protected request.
- It does not read a token from JSON.

Backend implication:

- Simple JWT's default refresh view is not enough for this frontend because it expects a JSON `refresh` value in the body.
- Implement a cookie-aware refresh view that reads `refresh_token`, creates a new access token, sets a new `access_token` cookie, and returns `{ "detail": "Token refreshed" }`.

## Quiz API Contract From Frontend

Endpoint constants:

```js
const CREATE_QUIZ_URL = "quizzes/";
const GET_QUIZ_URL = "quizzes/";
```

### POST `/api/quizzes/`

Called by `createQuiz(url)` from `library.js`.

Request body:

```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

Frontend behavior:

- Shows loading overlay while waiting.
- On success, expects a JSON object with an `id` field and redirects to `/pages/quizoverview.html?id=<id>`.
- On failure, shows generic `Error generating quiz`.

Backend implication:

- This endpoint may be slow due to download/transcription/Gemini.
- The frontend currently waits synchronously for the full response.
- Return the complete quiz object as documented.

### GET `/api/quizzes/`

Used by library cards, quiz sidebar, and all-quizzes overview.

Expected response shape:

```json
[
  {
    "id": 1,
    "title": "Quiz Title",
    "description": "Quiz Description",
    "created_at": "2023-07-29T12:34:56.789Z",
    "updated_at": "2023-07-29T12:34:56.789Z",
    "video_url": "https://www.youtube.com/watch?v=example",
    "questions": [
      {
        "id": 1,
        "question_title": "Question 1",
        "question_options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "Option A"
      }
    ]
  }
]
```

Frontend dependency details:

- `library.js` displays `quiz.title` and uses `quiz.id`.
- `quizoverview.js` filters by `created_at` using JavaScript `Date`.
- `quizoverview.js` expects `video_url` in canonical watch format and transforms it to an embed URL by extracting `v=...`.
- `quiz.js` expects `questions` to be an array.

### GET `/api/quizzes/{id}/`

Used by quiz overview and quiz play pages.

Required fields:

- `id`
- `title`
- `description`
- `created_at`
- `updated_at`
- `video_url`
- `questions`

Question fields required by frontend:

- `question_title`
- `question_options`
- `answer`

### PATCH `/api/quizzes/{id}/`

Called automatically while editing the quiz overview page.

Request body:

```json
{
  "title": "...",
  "description": "..."
}
```

Frontend behavior:

- Debounces by 1 second after keydown.
- Does not display detailed success/failure state.
- Expects updated quiz JSON if response is OK.

### DELETE `/api/quizzes/{id}/`

Used from the all-quizzes overview in `quiz.js`.

Frontend behavior:

- If response is OK, reloads quiz list.
- 204 is acceptable because `response.ok` is true.

## Canonical YouTube URL Requirement

The frontend derives the embed URL like this:

```js
const match = url.match(/v=([^&]+)/);
return `https://www.youtube.com/embed/${match[1]}`;
```

Therefore the backend must store `video_url` in this exact shape:

```text
https://www.youtube.com/watch?v=<video_id>
```

Do not store shortened URLs, embed URLs, playlist URLs, or raw submitted URLs.

## Current Backend Gap List

- [x] Add credentialed CORS support for the frontend origin.
- [x] Replace/default-wrap Simple JWT endpoints with cookie-aware auth views.
- [x] Add refresh-token blacklist support for logout.
- [x] Ensure cookies are named exactly `access_token` and `refresh_token`.
- [x] Ensure protected endpoints authenticate from cookies, not only `Authorization` headers.
- [x] Implement `/api/register/`, `/api/login/`, `/api/logout/`, `/api/token/refresh/` per frontend behavior.
- [x] Implement quiz CRUD endpoints with exact response field names.
- [x] Store canonical YouTube watch URLs.
- [x] Return ISO datetime strings parseable by JavaScript `Date`.
- [x] Keep question options as a JSON array of exactly four strings.
- [x] Keep `answer` equal to one of the `question_options` strings.

## Contract Verification (2026-07-18)

Verified against frontend commit `ae8e863` (cloned outside the project at
`C:\tmp\quizly-frontend`; the frontend repository must not live inside this
project).

Static verification, backend code matched against the frontend source:

- Endpoint URLs: `config/urls.py`, `accounts/urls.py`, and `quizzes_app/urls.py`
  expose exactly the routes `config.js` builds from `API_BASE_URL`.
- Cookie names and flags: `core/cookies.py` uses `access_token` /
  `refresh_token`, HttpOnly, SameSite=Lax.
- CORS: `corsheaders` middleware first, `CORS_ALLOWED_ORIGINS` defaults to
  `http://127.0.0.1:5500` and `http://localhost:5500`,
  `CORS_ALLOW_CREDENTIALS = True` (`config/settings.py`).
- Response bodies: register/login/logout/refresh payloads in
  `accounts/views.py` and `accounts/utils.py` match the messages and field
  names the frontend reads (`data.username`, `responseData.detail`,
  `user.{id,username,email}`).
- Quiz payloads: `QuizSerializer` / `QuestionSerializer` field names match the
  properties used by `library.js`, `quizoverview.js`, and `quiz.js`;
  `normalize_youtube_url` stores the canonical `watch?v=` shape the embed
  transformation requires.

Live verification: `manage.py runserver` plus a request-level probe replaying
the frontend flow (Origin `http://127.0.0.1:5500`, cookies only, no
`Authorization` header). All 21 checks passed: CORS preflight, register (201 +
detail), login (200, HttpOnly cookie pair, `detail` + `user` body, no tokens
in JSON), protected quiz list via cookies, body-less token refresh (rotated
`access_token` cookie, `Token refreshed`), logout (cookies cleared), and a 401
on the quiz list after logout.

No frontend mismatch remains.
