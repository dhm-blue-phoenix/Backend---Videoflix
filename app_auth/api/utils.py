from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django_rq import enqueue
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from ..tasks import send_activation_email_task, send_password_reset_email_task

User = get_user_model()

def create_user(data):
    """Validates data and creates a new inactive user."""
    _validate_registration_data(data)
    user = User.objects.create_user(email=data.get('email'), password=data.get('password'))
    enqueue(send_activation_email_task, user.id)
    return {
        "user": {"id": user.id, "email": user.email},
        "token": "activation_token"
    }

def _validate_registration_data(data):
    """Helper for create_user to keep it under 14 lines."""
    email, pw, confirm = data.get('email'), data.get('password'), data.get('confirmed_password')
    if not all([email, pw, confirm]):
        raise ValidationError({"detail": "All fields are required."})
    if pw != confirm:
        raise ValidationError({"detail": "Passwords do not match."})
    if User.objects.filter(email=email).exists():
        raise ValidationError({"detail": "User already exists."})
    return True

def authenticate_and_get_tokens(email, password):
    """Authenticates user via email and returns JWT tokens."""
    if not email or not password:
        raise AuthenticationFailed({"detail": "Credentials required."})
    user = authenticate(email=email, password=password)
    if user is None or not user.is_active:
        raise AuthenticationFailed({"detail": "Invalid credentials or inactive account."})
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token), 'refresh': str(refresh),
        'user': {'id': user.id, 'username': user.email}
    }

def guest_login():
    """Returns tokens for a persistent guest user."""
    user, _ = User.objects.get_or_create(
        email="guest@videoflix.com", defaults={'is_active': True, 'username': 'GuestUser'}
    )
    if not user.is_active:
        user.is_active = True
        user.save()
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token), 'refresh': str(refresh),
        'user': {'id': user.id, 'username': user.email}
    }

def set_auth_cookies(response, access_token, refresh_token):
    """Sets HTTPOnly cookies with appropriate security flags."""
    secure = settings.DEBUG is False
    response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=secure)
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=secure)
    return response

def delete_auth_cookies(response):
    """Clears authentication cookies."""
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

def blacklist_refresh_token(request):
    """Blacklists the refresh token from the cookie."""
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except: pass

def refresh_access_token(request):
    """Generates a new access token from the refresh token cookie."""
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        raise AuthenticationFailed({"detail": "Refresh token missing."})
    try:
        return str(RefreshToken(refresh_token).access_token)
    except:
        raise AuthenticationFailed({"detail": "Invalid refresh token."})

def initiate_password_reset(email):
    """Enqueues reset email if user exists. Always returns success."""
    try:
        user = User.objects.get(email=email)
        enqueue(send_password_reset_email_task, user.id)
    except User.DoesNotExist:
        pass
    return {"detail": "An email has been sent to reset your password."}

def confirm_password_reset(data, uidb64, token):
    """Validates token and updates user password."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except: raise ValidationError({"detail": "Invalid reset link."})
    if not default_token_generator.check_token(user, token):
        raise ValidationError({"detail": "Token invalid or expired."})
    password, confirm = data.get('new_password'), data.get('confirm_password')
    if not password or password != confirm:
        raise ValidationError({"detail": "Passwords missing or do not match."})
    user.set_password(password)
    user.save()

def verify_activation(uidb64, token):
    """Verifies activation token and activates user."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except: raise ValidationError({"detail": "Invalid activation link."})
    if not default_token_generator.check_token(user, token):
        raise ValidationError({"detail": "Activation token invalid or expired."})
    user.is_active = True
    user.save()
