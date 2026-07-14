from importlib import import_module

from django.apps import apps


def test_domain_apps_are_registered():
    assert apps.is_installed('core')
    assert apps.is_installed('accounts')
    assert apps.is_installed('quizzes')


def test_domain_app_configs_import_cleanly():
    assert import_module('core.apps').CoreConfig.name == 'core'
    assert import_module('accounts.apps').AccountsConfig.name == 'accounts'
    assert import_module('quizzes.apps').QuizzesConfig.name == 'quizzes'
