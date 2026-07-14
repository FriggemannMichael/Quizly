from django.urls import reverse


def test_jwt_token_urls_are_registered():
    assert reverse('token_obtain_pair') == '/api/token/'
    assert reverse('token_refresh') == '/api/token/refresh/'
