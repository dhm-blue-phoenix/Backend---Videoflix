from django.apps import AppConfig


class AppVideoflixConfig(AppConfig):
    name = 'app_content'

    def ready(self):
        from . import singals


## !! app import bei settings.py | 'app_content.apps.ContentConfig',