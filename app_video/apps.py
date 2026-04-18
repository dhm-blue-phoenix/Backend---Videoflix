from django.apps import AppConfig


class AppVideoConfig(AppConfig):
    """
    Manages video content, including metadata storage, automated HLS conversion, 
    thumbnail extraction, and authenticated media streaming.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_video'

    def ready(self):
        from . import signals