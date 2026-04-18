import subprocess, os
from django.conf import settings
from django_rq import enqueue
from .models import Video

def process_video_task(video_id):
    """Main task to initiate all video processing steps."""
    video = Video.objects.get(id=video_id)
    video.processing_status = 'PROCESSING'
    video.save()
    enqueue(extract_thumbnail_task, video_id)
    for res in ['480p', '720p', '1080p']:
        enqueue(convert_to_hls_task, video_id, res)

def extract_thumbnail_task(video_id):
    """Extracts a thumbnail from the video at 1 second mark."""
    video = Video.objects.get(id=video_id)
    out_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'thumb_{video_id}.jpg')
    cmd = f'ffmpeg -i "{video.video_file.path}" -ss 00:00:01 -vframes 1 "{out_path}" -y'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        _handle_thumbnail_result(video, result, video_id)
    except Exception as e:
        _set_video_error(video, f"Extraction failed: {e}")

def _handle_thumbnail_result(video, result, video_id):
    """Helper to handle FFmpeg result for thumbnail extraction."""
    if result.returncode == 0:
        video.thumbnail.name = f'thumbnails/thumb_{video_id}.jpg'
        video.save()
    else:
        _set_video_error(video, f"FFmpeg error: {result.stderr}")

def convert_to_hls_task(video_id, res):
    """Converts video to a specific HLS resolution."""
    video = Video.objects.get(id=video_id)
    out_dir = os.path.join(settings.MEDIA_ROOT, 'hls', f'video_{video_id}', res)
    os.makedirs(out_dir, exist_ok=True)
    scale = {'480p': 'scale=-2:480', '720p': 'scale=-2:720', '1080p': 'scale=-2:1080'}[res]
    cmd = f'ffmpeg -i "{video.video_file.path}" -vf {scale} -c:v libx264 -crf 23 ' \
          f'-c:a aac -hls_time 10 -hls_list_size 0 -hls_segment_filename ' \
          f'"{out_dir}/seg_%03d.ts" "{out_dir}/index.m3u8" -y'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        _handle_conversion_result(video, result, video_id, res)
    except Exception as e:
        _set_video_error(video, f"Conversion failed ({res}): {e}")

def _handle_conversion_result(video, result, video_id, res):
    """Helper to handle FFmpeg result for HLS conversion."""
    if result.returncode == 0:
        check_all_done(video_id)
    else:
        _set_video_error(video, f"FFmpeg conversion error ({res}): {result.stderr}")

def _set_video_error(video, error_msg):
    """Helper to set video status to ERROR and log the message."""
    print(error_msg)
    video.processing_status = 'ERROR'
    video.save()

def check_all_done(video_id):
    """Sets status to DONE and creates master playlist if all resolutions exist."""
    video = Video.objects.get(id=video_id)
    base_dir = os.path.join(settings.MEDIA_ROOT, 'hls', f'video_{video_id}')
    resolutions = ['480p', '720p', '1080p']
    if all(os.path.exists(os.path.join(base_dir, r, 'index.m3u8')) for r in resolutions):
        create_master_playlist(video, base_dir)
        video.processing_status = 'DONE'
        video.save()

def create_master_playlist(video, base_dir):
    """Generates the master.m3u8 file linking all resolutions."""
    master_path = os.path.join(base_dir, 'master.m3u8')
    content = "#EXTM3U\n#EXT-X-VERSION:3\n"
    content += "#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x480\n480p/index.m3u8\n"
    content += "#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=1280x720\n720p/index.m3u8\n"
    content += "#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1920x1080\n1080p/index.m3u8\n"
    with open(master_path, 'w') as f:
        f.write(content)