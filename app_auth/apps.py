from django.apps import AppConfig

class AppAuthConfig(AppConfig):
    """
    Handles user authentication, registration, account activation, 
    and password management using JWT with HTTP-only cookies.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_auth'
