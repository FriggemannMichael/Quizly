from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import LoginSerializer, RegisterSerializer
from core.cookies import set_auth_cookies


class RegisterView(APIView):
    """Create users from public registration requests."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'User created successfully!'},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate users and set JWT auth cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = _validated_login_serializer(request)
        user = serializer.validated_data['user']
        refresh_token = RefreshToken.for_user(user)
        response = Response(_login_response_payload(user))
        set_auth_cookies(response, str(refresh_token.access_token), str(refresh_token))
        return response


def _validated_login_serializer(request):
    serializer = LoginSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        raise AuthenticationFailed('Invalid credentials.')
    return serializer


def _login_response_payload(user):
    return {
        'detail': 'Login successfully!',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
    }
