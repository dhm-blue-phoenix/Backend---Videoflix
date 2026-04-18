from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse, Http404
from ..models import Video
from .serializers import VideoSerializer
from .utils import get_hls_file_path

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_list_view(request):
    """Returns a list of all videos sorted by creation date."""
    videos = Video.objects.filter(processing_status='DONE').order_by('-created_at')
    serializer = VideoSerializer(videos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def master_hls_view(request, movie_id, resolution):
    """Serves the master.m3u8 file for adaptive streaming."""
    try:
        Video.objects.get(id=movie_id)
        file_path = get_hls_file_path(movie_id, resolution, 'index.m3u8')
        return FileResponse(open(file_path, 'rb'))
    except Video.DoesNotExist: raise Http404()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hls_proxy_view(request, movie_id, resolution, segment):
    """Serves HLS files (.m3u8 and .ts) if authenticated."""
    try:
        Video.objects.get(id=movie_id)
        file_path = get_hls_file_path(movie_id, resolution, segment)
        return FileResponse(open(file_path, 'rb'))
    except Video.DoesNotExist: raise Http404()
