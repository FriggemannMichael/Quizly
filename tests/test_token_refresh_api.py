import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core import cookies


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def refresh_token(db):
    user = get_user_model().objects.create_user(
        username='refresh_user',
        email='refresh-user@example.com',
        password='Str0ng-test-pass!',
    )
    return RefreshToken.for_user(user)


@pytest.mark.django_db
def test_token_refresh_uses_refresh_cookie_without_body(api_client, refresh_token):
    api_client.cookies[cookies.REFRESH_TOKEN_COOKIE_NAME] = str(refresh_token)

    response = api_client.post(reverse('token_refresh'), {}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'detail': 'Token refreshed'}
    access_cookie = response.cookies[cookies.ACCESS_TOKEN_COOKIE_NAME]
    assert access_cookie.value
    assert access_cookie['httponly'] is True
    assert access_cookie['samesite'] == cookies.AUTH_COOKIE_SAMESITE
    assert cookies.REFRESH_TOKEN_COOKIE_NAME not in response.cookies


@pytest.mark.django_db
def test_token_refresh_rejects_missing_refresh_cookie(api_client):
    response = api_client.post(reverse('token_refresh'), {}, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid refresh token.'}
    assert cookies.ACCESS_TOKEN_COOKIE_NAME not in response.cookies


@pytest.mark.django_db
def test_token_refresh_rejects_invalid_refresh_cookie(api_client):
    api_client.cookies[cookies.REFRESH_TOKEN_COOKIE_NAME] = 'not-a-jwt'

    response = api_client.post(reverse('token_refresh'), {}, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid refresh token.'}
    assert cookies.ACCESS_TOKEN_COOKIE_NAME not in response.cookies
