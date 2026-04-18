from django.apps import AppConfig


class AppVideoConfig(AppConfig):
    name = 'app_video'

    def ready(self):
        from . import signals


## !! app import bei settings.py | 'app_video.apps.ContentConfig',