from pathlib import Path

from dotenv import load_dotenv

ENV_FILE_NAME = '.env'


def load_env_file(base_dir: Path) -> None:
    """Load the project `.env` file into the process environment.

    Real environment variables take precedence, so CI and production stay
    authoritative over a developer's local file. A missing file is ignored.
    """
    load_dotenv(base_dir / ENV_FILE_NAME, override=False)
