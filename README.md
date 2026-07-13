# Quizly

## Local setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python main.py
```

## Code quality

```powershell
ruff check .
ruff format .
python scripts/check_size_limits.py
```

## CI

GitHub Actions runs the same checks on pushes and pull requests to `main`.

