from django.urls import reverse


def test_jwt_token_urls_are_registered():
    assert reverse('token_obtain_pair') == '/api/token/'
    assert reverse('token_refresh') == '/api/token/refresh/'


def test_register_url_is_registered():
    assert reverse('register') == '/api/register/'


def test_login_url_is_registered():
    assert reverse('login') == '/api/login/'
