import os
from django.conf import settings

def get_hls_base_dir(movie_id):
    """Returns the absolute path to the HLS directory for a video."""
    return os.path.join(settings.MEDIA_ROOT, 'hls', f'video_{movie_id}')

def get_hls_file_path(movie_id, resolution, filename):
    """Resolves the absolute path to a specific HLS file or segment."""
    base_dir = get_hls_base_dir(movie_id)
    path = os.path.join(base_dir, resolution, filename)
    if not os.path.exists(path):
        from django.http import Http404
        raise Http404()
    return path
