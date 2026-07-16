import os

import pytest

from config.env import load_env_file


@pytest.fixture(autouse=True)
def restore_environ():
    """Undo environment changes that loading a .env file causes."""
    snapshot = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(snapshot)


def _write_env(base_dir, content):
    """Write a .env file into the given project directory."""
    (base_dir / '.env').write_text(content, encoding='utf-8')


def test_values_from_env_file_reach_the_environment(tmp_path):
    _write_env(tmp_path, 'GEMINI_API_KEY=key-from-file\n')

    load_env_file(tmp_path)

    assert os.environ['GEMINI_API_KEY'] == 'key-from-file'


def test_real_environment_wins_over_env_file(tmp_path):
    os.environ['GEMINI_API_KEY'] = 'key-from-shell'
    _write_env(tmp_path, 'GEMINI_API_KEY=key-from-file\n')

    load_env_file(tmp_path)

    assert os.environ['GEMINI_API_KEY'] == 'key-from-shell'


def test_missing_env_file_is_not_an_error(tmp_path):
    os.environ.pop('GEMINI_API_KEY', None)

    load_env_file(tmp_path)

    assert 'GEMINI_API_KEY' not in os.environ


def test_env_file_may_define_several_variables(tmp_path):
    _write_env(tmp_path, 'DJANGO_DEBUG=false\nDJANGO_SECRET_KEY=secret\n')

    load_env_file(tmp_path)

    assert os.environ['DJANGO_DEBUG'] == 'false'
    assert os.environ['DJANGO_SECRET_KEY'] == 'secret'
