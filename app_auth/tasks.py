from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string

User = get_user_model()

def send_email_activation_task(user_id):
    """Refactored activation email task to follow 14-line rule."""
    user = User.objects.get(id=user_id)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    name = user.username or user.email.split('@')[0]
    url = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uid}&token={token}"
    subject = "Aktiviere deinen Videoflix Account"
    ctx = {'url': url, 'frontend_url': settings.FRONTEND_URL, 'backend_url': settings.BACKEND_URL, 'name': name}
    html_msg = render_to_string('app_auth/email_activation.html', ctx)
    return send_mail(subject, "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_msg)

def send_email_password_reset_task(user_id):
    """Background task to send password reset email in German."""
    user = User.objects.get(id=user_id)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uid}&token={token}"
    subject = "Passwort zurücksetzen - Videoflix"
    ctx = {'url': url, 'frontend_url': settings.FRONTEND_URL, 'backend_url': settings.BACKEND_URL}
    html_msg = render_to_string('app_auth/email_password_reset.html', ctx)
    return send_mail(subject, "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_msg)
