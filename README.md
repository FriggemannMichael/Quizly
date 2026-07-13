# Quizly

## Local setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

## Code quality

```powershell
ruff check .
ruff format .
python scripts/check_size_limits.py
pytest
```

## CI

GitHub Actions runs the same checks on pushes and pull requests to `main`.

## Django

The project uses Django 5.2 with the settings module `config.settings`.
Local SQLite data is stored in `db.sqlite3` and ignored by Git.

