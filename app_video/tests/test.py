from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Video

User = get_user_model()

class ContentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="content@example.com", password="Password123!", is_active=True)
        self.client.force_authenticate(user=self.user)
        self.video_list_url = reverse('video_list')
        
    def test_video_model_creation(self):
        """Tests that a Video object can be created with valid data."""
        video = Video.objects.create(
            title="Test Video",
            description="Description",
            category="ACTION",
            video_file=SimpleUploadedFile("test.mp4", b"content", content_type="video/mp4")
        )
        self.assertEqual(video.title, "Test Video")
        self.assertEqual(video.processing_status, "PENDING")

    def test_video_list_authenticated(self):
        """Happy Path: Authenticated user can list videos."""
        Video.objects.create(title="V1", category="ACTION", processing_status="DONE")
        response = self.client.get(self.video_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('thumbnail_url', response.data[0])
        self.assertEqual(len(response.data), 1)

    def test_video_list_unauthorized(self):
        """Unhappy Path: Anonymous user cannot list videos."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.video_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_hls_proxy_not_found(self):
        """Unhappy Path: HLS proxy returns 404 for missing video/path."""
        url = reverse('hls_proxy', kwargs={'movie_id': 999, 'resolution': '480p', 'segment': '000.ts'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
