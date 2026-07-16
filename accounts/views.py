from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import RegisterSerializer
from accounts.utils import (
    login_response_payload,
    logout_response_payload,
    validated_login_serializer,
    validated_refresh_token,
)
from core.cookies import (
    delete_auth_cookies,
    set_access_token_cookie,
    set_auth_cookies,
)


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
        serializer = validated_login_serializer(request)
        user = serializer.validated_data['user']
        refresh_token = RefreshToken.for_user(user)
        response = Response(login_response_payload(user))
        set_auth_cookies(response, str(refresh_token.access_token), str(refresh_token))
        return response


class LogoutView(APIView):
    """Blacklist the refresh token and clear the auth cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = validated_refresh_token(request)
        refresh_token.blacklist()
        response = Response(logout_response_payload())
        delete_auth_cookies(response)
        return response


class CookieTokenRefreshView(APIView):
    """Refresh the access token from the refresh token cookie."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = validated_refresh_token(request)
        response = Response({'detail': 'Token refreshed'})
        set_access_token_cookie(response, str(refresh_token.access_token))
        return response
