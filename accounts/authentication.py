from rest_framework_simplejwt.authentication import JWTAuthentication

from core.cookies import ACCESS_TOKEN_COOKIE_NAME


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests carrying their access token in a cookie.

    The frontend stores JWTs in HttpOnly cookies and never sends an
    Authorization header, so the header check alone would reject it.
    """

    def authenticate(self, request):
        """Return the user for the Authorization header or the access cookie."""
        authenticated = super().authenticate(request)
        if authenticated is not None:
            return authenticated
        return self._authenticate_from_cookie(request)

    def _authenticate_from_cookie(self, request):
        """Return the user for the access token cookie, if the request has one."""
        raw_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE_NAME)
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
