import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core import cookies


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username='quiz_user',
        email='quiz-user@example.com',
        password='Str0ng-test-pass!',
    )


@pytest.mark.django_db
def test_login_sets_auth_cookies_and_returns_user(api_client, user):
    response = api_client.post(
        reverse('login'),
        {'username': user.username, 'password': 'Str0ng-test-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'detail': 'Login successfully!',
        'user': {
            'id': user.id,
            'username': 'quiz_user',
            'email': 'quiz-user@example.com',
        },
    }
    access_cookie = response.cookies[cookies.ACCESS_TOKEN_COOKIE_NAME]
    refresh_cookie = response.cookies[cookies.REFRESH_TOKEN_COOKIE_NAME]
    assert access_cookie.value
    assert refresh_cookie.value
    assert access_cookie['httponly'] is True
    assert refresh_cookie['httponly'] is True
    assert access_cookie['samesite'] == cookies.AUTH_COOKIE_SAMESITE
    assert refresh_cookie['samesite'] == cookies.AUTH_COOKIE_SAMESITE


@pytest.mark.django_db
def test_login_rejects_invalid_credentials(api_client, user):
    response = api_client.post(
        reverse('login'),
        {'username': user.username, 'password': 'wrong-password'},
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid credentials.'}
    assert cookies.ACCESS_TOKEN_COOKIE_NAME not in response.cookies
    assert cookies.REFRESH_TOKEN_COOKIE_NAME not in response.cookies
