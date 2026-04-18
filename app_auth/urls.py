"""
Bridge URL configuration for app_auth.
Redirects to the internal api/urls.py.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('app_auth.api.urls')),
]
