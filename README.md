# Quizly

## Local setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Code quality

```powershell
ruff check .
ruff format .
python tests/scripts/check_size_limits.py
pytest
```

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

## External Requirements

FFmpeg must be installed globally for the future Whisper audio transcription workflow.
