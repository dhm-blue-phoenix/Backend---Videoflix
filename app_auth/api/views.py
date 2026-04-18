"""
Views for the authentication API. All views delegate logic to functions.py.
Each view adheres strictly to the 14-line rule for Clean Code.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from .utils import (
    create_user, authenticate_and_get_tokens, set_auth_cookies,
    delete_auth_cookies, blacklist_refresh_token, refresh_access_token, guest_login,
    initiate_password_reset, confirm_password_reset, verify_activation
)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Registers a new user and enqueues activation email."""
    res_data = create_user(request.data)
    return Response(res_data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def activation_view(request, uidb64, token):
    """Activates a user account if the token is valid."""
    verify_activation(uidb64, token)
    return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Authenticates user via email and returns JWT cookies."""
    data = authenticate_and_get_tokens(request.data.get('email'), request.data.get('password'))
    res = Response({"detail": "Login successful", "user": data['user']}, status=status.HTTP_200_OK)
    return set_auth_cookies(res, data['access'], data['refresh'])

@api_view(['POST'])
@permission_classes([AllowAny])
def guest_login_view(request):
    """Logs in a guest user for instant access."""
    data = guest_login()
    res = Response({"detail": "Guest login successful", "user": data['user']}, status=status.HTTP_200_OK)
    return set_auth_cookies(res, data['access'], data['refresh'])

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logs out user by blacklisting tokens and clearing cookies."""
    blacklist_refresh_token(request)
    msg = "Logout successful! All tokens will be deleted. Refresh token is now invalid."
    return delete_auth_cookies(Response({"detail": msg}, status=status.HTTP_200_OK))

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """Refreshes the access token using the refresh cookie."""
    new_access = refresh_access_token(request)
    res = Response({"detail": "Token refreshed", "access": new_access}, status=status.HTTP_200_OK)
    return set_auth_cookies(res, new_access, request.COOKIES.get('refresh_token'))

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_view(request):
    """Initiates password reset flow."""
    res = initiate_password_reset(request.data.get('email'))
    return Response(res, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request, uidb64, token):
    """Confirms password reset for a user."""
    confirm_password_reset(request.data, uidb64, token)
    return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)
