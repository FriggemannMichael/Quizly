from django.http import JsonResponse

from core import cookies


def test_auth_cookie_names_match_frontend_contract():
    assert cookies.ACCESS_TOKEN_COOKIE_NAME == 'access_token'
    assert cookies.REFRESH_TOKEN_COOKIE_NAME == 'refresh_token'


def test_set_auth_cookies_sets_secure_http_only_cookies():
    response = JsonResponse({})

    cookies.set_auth_cookies(response, 'access.jwt', 'refresh.jwt')

    access_cookie = response.cookies['access_token']
    refresh_cookie = response.cookies['refresh_token']
    assert access_cookie.value == 'access.jwt'
    assert refresh_cookie.value == 'refresh.jwt'
    assert access_cookie['httponly'] is True
    assert refresh_cookie['httponly'] is True
    assert access_cookie['samesite'] == cookies.AUTH_COOKIE_SAMESITE
    assert refresh_cookie['samesite'] == cookies.AUTH_COOKIE_SAMESITE
    assert bool(access_cookie['secure']) is cookies.AUTH_COOKIE_SECURE
    assert bool(refresh_cookie['secure']) is cookies.AUTH_COOKIE_SECURE


def test_delete_auth_cookies_expires_auth_cookies():
    response = JsonResponse({})

    cookies.delete_auth_cookies(response)

    assert response.cookies['access_token']['max-age'] == 0
    assert response.cookies['refresh_token']['max-age'] == 0
