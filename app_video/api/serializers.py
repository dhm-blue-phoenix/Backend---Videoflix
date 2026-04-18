from rest_framework import serializers
from django.conf import settings
from ..models import Video

class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Video model with absolute thumbnail URL mapping."""
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Metadata for the VideoSerializer, specifying model and field mapping."""
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']

    def get_thumbnail_url(self, obj):
        """Returns the absolute URL for the video thumbnail if it exists."""
        if obj.thumbnail:
            return f"{settings.BACKEND_URL}{obj.thumbnail.url}"
        return None
