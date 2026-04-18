from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_rq import enqueue
import os
from .models import Video
from .tasks import process_video_task

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """Triggers HLS processing when a new video is uploaded."""
    if created:
        enqueue(process_video_task, instance.id)

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Cleans up original video file when Video object is deleted."""
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)