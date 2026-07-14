from django.http import HttpResponse

ACCESS_TOKEN_COOKIE_NAME = 'access_token'
REFRESH_TOKEN_COOKIE_NAME = 'refresh_token'
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_SAMESITE = 'Lax'
AUTH_COOKIE_SECURE = False


def set_auth_cookies(
    response: HttpResponse, access_token: str, refresh_token: str
) -> None:
    set_access_token_cookie(response, access_token)
    set_refresh_token_cookie(response, refresh_token)


def set_access_token_cookie(response: HttpResponse, token: str) -> None:
    _set_cookie(response, ACCESS_TOKEN_COOKIE_NAME, token)


def set_refresh_token_cookie(response: HttpResponse, token: str) -> None:
    _set_cookie(response, REFRESH_TOKEN_COOKIE_NAME, token)


def delete_auth_cookies(response: HttpResponse) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, samesite=AUTH_COOKIE_SAMESITE)
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, samesite=AUTH_COOKIE_SAMESITE)


def _set_cookie(response: HttpResponse, name: str, value: str) -> None:
    response.set_cookie(
        name,
        value,
        httponly=AUTH_COOKIE_HTTP_ONLY,
        samesite=AUTH_COOKIE_SAMESITE,
        secure=AUTH_COOKIE_SECURE,
    )
