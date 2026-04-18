from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

def send_activation_email_task(user_id):
    """Refactored activation email task to follow 14-line rule."""
    user = User.objects.get(id=user_id)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uid}&token={token}"
    subject = "Aktiviere deinen Videoflix Account"
    message = f"Willkommen! Bitte aktiviere deinen Account unter: {url}"
    return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_password_reset_email_task(user_id):
    """Background task to send password reset email in German."""
    user = User.objects.get(id=user_id)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = f"{settings.FRONTEND_URL}/pages/auth/password_reset.html?uid={uid}&token={token}"
    subject = "Passwort zurücksetzen - Videoflix"
    message = f"Hallo, setze dein Passwort hier zurück: {url}"
    return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
