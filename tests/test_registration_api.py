import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_creates_user(api_client):
    response = api_client.post(
        reverse('register'),
        {
            'username': 'new_user',
            'email': 'new-user@example.com',
            'password': 'Str0ng-test-pass!',
            'confirmed_password': 'Str0ng-test-pass!',
        },
        format='json',
    )

    user = get_user_model().objects.get(username='new_user')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {'detail': 'User created successfully!'}
    assert user.email == 'new-user@example.com'
    assert user.check_password('Str0ng-test-pass!')


@pytest.mark.django_db
def test_register_rejects_password_mismatch(api_client):
    response = api_client.post(
        reverse('register'),
        {
            'username': 'new_user',
            'email': 'new-user@example.com',
            'password': 'Str0ng-test-pass!',
            'confirmed_password': 'different-pass',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'confirmed_password' in response.json()
    assert not get_user_model().objects.filter(username='new_user').exists()


@pytest.mark.django_db
def test_register_rejects_duplicate_username(api_client):
    get_user_model().objects.create_user(
        username='existing_user',
        email='existing@example.com',
        password='Str0ng-test-pass!',
    )

    response = api_client.post(
        reverse('register'),
        {
            'username': 'existing_user',
            'email': 'other@example.com',
            'password': 'Str0ng-test-pass!',
            'confirmed_password': 'Str0ng-test-pass!',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.json()


@pytest.mark.django_db
def test_register_rejects_duplicate_email(api_client):
    get_user_model().objects.create_user(
        username='existing_user',
        email='existing@example.com',
        password='Str0ng-test-pass!',
    )

    response = api_client.post(
        reverse('register'),
        {
            'username': 'other_user',
            'email': 'existing@example.com',
            'password': 'Str0ng-test-pass!',
            'confirmed_password': 'Str0ng-test-pass!',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.json()
