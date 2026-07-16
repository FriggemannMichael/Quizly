import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core import cookies

LOGOUT_DETAIL = (
    'Log-Out successfully! All Tokens will be deleted. '
    'Refresh token is now invalid.'
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def refresh_token(db):
    user = get_user_model().objects.create_user(
        username='logout_user',
        email='logout-user@example.com',
        password='Str0ng-test-pass!',
    )
    return RefreshToken.for_user(user)


@pytest.mark.django_db
def test_logout_clears_cookies_and_returns_detail(api_client, refresh_token):
    api_client.cookies[cookies.REFRESH_TOKEN_COOKIE_NAME] = str(refresh_token)

    response = api_client.post(reverse('logout'), {}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'detail': LOGOUT_DETAIL}
    assert response.cookies[cookies.ACCESS_TOKEN_COOKIE_NAME].value == ''
    assert response.cookies[cookies.REFRESH_TOKEN_COOKIE_NAME].value == ''


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(api_client, refresh_token):
    api_client.cookies[cookies.REFRESH_TOKEN_COOKIE_NAME] = str(refresh_token)
    api_client.post(reverse('logout'), {}, format='json')

    api_client.cookies[cookies.REFRESH_TOKEN_COOKIE_NAME] = str(refresh_token)
    refresh_response = api_client.post(reverse('token_refresh'), {}, format='json')

    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert refresh_response.json() == {'detail': 'Invalid refresh token.'}


@pytest.mark.django_db
def test_logout_rejects_missing_refresh_cookie(api_client):
    response = api_client.post(reverse('logout'), {}, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid refresh token.'}


@pytest.mark.django_db
def test_logout_rejects_invalid_refresh_cookie(api_client):
    api_client.cookies[cookies.REFRESH_TOKEN_COOKIE_NAME] = 'not-a-jwt'

    response = api_client.post(reverse('logout'), {}, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid refresh token.'}
