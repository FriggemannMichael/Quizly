from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import LoginSerializer
from core.cookies import REFRESH_TOKEN_COOKIE_NAME


def validated_login_serializer(request):
    """Return a validated login serializer or raise on bad credentials."""
    serializer = LoginSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        raise AuthenticationFailed('Invalid credentials.')
    return serializer


def validated_refresh_token(request):
    """Return the refresh token from the request cookie or raise if invalid."""
    token = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)
    if token is None:
        raise AuthenticationFailed('Invalid refresh token.')
    try:
        return RefreshToken(token)
    except TokenError as error:
        raise AuthenticationFailed('Invalid refresh token.') from error


def login_response_payload(user):
    """Build the JSON payload returned after a successful login."""
    return {
        'detail': 'Login successfully!',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
    }
