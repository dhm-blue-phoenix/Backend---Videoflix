import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from app_video.models import Video
from django.core.exceptions import ValidationError

class VideoValidationTest(TestCase):
    def test_invalid_extension(self):
        """Verify that invalid file extensions are rejected by the model."""
        video = Video(
            title="Invalid Test",
            description="Testing validation",
            category="ACTION",
            video_file=SimpleUploadedFile("test.txt", b"dummy content", content_type="text/plain")
        )
        with self.assertRaises(ValidationError):
            video.full_clean()

    def test_valid_extension(self):
        """Verify that valid file extensions are accepted."""
        video = Video(
            title="Valid Test",
            description="Testing validation",
            category="ACTION",
            video_file=SimpleUploadedFile("test.mp4", b"dummy content", content_type="video/mp4")
        )
        try:
            video.full_clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for .mp4 file")
