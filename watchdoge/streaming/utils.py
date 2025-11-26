import uuid
import os
import shutil
from django.conf import settings
#import subprocess

def movie_file_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # preserves .mp4, .mkv, etc.
    unique_name = uuid.uuid4().hex + ext
    return f'movies/files/{unique_name}'

def poster_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # preserves .jpg, .png, etc.
    unique_name = uuid.uuid4().hex + ext
    return f'movies/posters/{unique_name}'


def delete_old_file(instance, field_name):
    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
        old_file = getattr(old_instance, field_name)
        new_file = getattr(instance, field_name)

        if old_file != new_file and old_file.name != 'profile_pictures/default_icon.png':
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except instance.__class__.DoesNotExist:
        pass


def delete_original_after_conversion(movie):
    """Delete the original uploaded file once HLS conversion succeeds."""
    if movie.file and os.path.isfile(movie.file.path):
        try:
            os.remove(movie.file.path)
            print(f"[CLEANUP] Deleted original file: {movie.file.path}")
        except Exception as e:
            print(f"[CLEANUP] Could not delete {movie.file.path}: {e}")

    # Clear reference in DB
    movie.file = None
    movie.save(update_fields=['file'])


def delete_hls_folder(movie):
    """Delete the HLS folder for a movie (if exists)."""
    if movie.hls_path:
        hls_folder = os.path.dirname(os.path.join(settings.MEDIA_ROOT, movie.hls_path))
        if os.path.isdir(hls_folder):
            try:
                shutil.rmtree(hls_folder)
                print(f"[CLEANUP] Deleted HLS folder: {hls_folder}")
            except Exception as e:
                print(f"[CLEANUP] Could not delete HLS folder {hls_folder}: {e}")
