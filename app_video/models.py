from django.db import models
from django.core.validators import FileExtensionValidator

class Video(models.Model):
    """Represents a video content with HLS streaming support."""
    GENRE_CHOICES = [
        ('ACTION', 'Action'), ('COMEDY', 'Comedy'), ('DRAMA', 'Drama'),
        ('HORROR', 'Horror'), ('DOCUMENTARY', 'Documentary')
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('PROCESSING', 'Processing'),
        ('DONE', 'Done'), ('ERROR', 'Error')
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=GENRE_CHOICES)
    video_file = models.FileField(
        upload_to='videos/originals/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'avi', 'mov'])]
    )
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_highlight = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return self.title
