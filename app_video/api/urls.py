from django.urls import path
from .views import video_list_view, hls_proxy_view, master_hls_view

urlpatterns = [
    path('', video_list_view, name='video_list'),
    path('<int:movie_id>/<str:resolution>/index.m3u8', master_hls_view, name='hls_master'),
    path('<int:movie_id>/<str:resolution>/<str:segment>', hls_proxy_view, name='hls_proxy'),
]
