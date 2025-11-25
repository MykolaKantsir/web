"""
API views for token-based authentication.
These endpoints allow Android apps to authenticate without CSRF tokens.
"""
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate


class CustomAuthToken(ObtainAuthToken):
    """
    Custom token authentication endpoint for Android app.

    POST /api/auth/login/
    Body: {"username": "user", "password": "pass"}
    Returns: {"token": "abc123...", "user_id": 1, "username": "user"}
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user'] #type: ignore
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        })


class LogoutView(APIView):
    """
    Logout endpoint that deletes the user's token.
    Requires authentication via token.

    POST /api/auth/logout/
    Header: Authorization: Token abc123...
    Returns: {"message": "Successfully logged out"}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValidateTokenView(APIView):
    """
    Endpoint to validate if a token is still valid.

    GET /api/auth/validate/
    Header: Authorization: Token abc123...
    Returns: {"valid": true, "user_id": 1, "username": "user"}
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'valid': True,
            'user_id': request.user.pk,
            'username': request.user.username,
            'email': request.user.email
        })
