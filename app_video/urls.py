from django.urls import path, include

urlpatterns = [
    path('video/', include('app_video.api.urls')),
]
