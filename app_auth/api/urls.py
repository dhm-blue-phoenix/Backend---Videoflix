from django.urls import path
from .views import (
    register_view, login_view, logout_view, refresh_token_view, 
    guest_login_view, activation_view, password_reset_view, password_reset_confirm_view
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('activate/<str:uidb64>/<str:token>/', activation_view, name='activate'),
    path('login/', login_view, name='login'),
    path('login/guest/', guest_login_view, name='guest_login'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', refresh_token_view, name='token_refresh'),
    path('password_reset/', password_reset_view, name='password_reset'),
    path('password_confirm/<str:uidb64>/<str:token>/', password_reset_confirm_view, name='password_confirm'),
]
